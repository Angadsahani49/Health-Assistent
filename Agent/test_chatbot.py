"""
Automated Test Suite for the Health Awareness Assistant.
Validates safety guardrails, emergency detection, diagnostic refusals,
quiz evaluation, and Flask web API endpoints.
"""

import os
import json
import tempfile
import unittest
from health_assistant import HealthChatbot, QUIZ_QUESTIONS, load_env, find_env_file
from health_assistant.env_loader import parse_env_file
from app import app


class TestHealthChatbot(unittest.TestCase):
    """Unit tests for the core chatbot logic and safety filters."""

    def setUp(self):
        self.bot = HealthChatbot()

    def test_emergency_detection(self):
        """Verify that acute emergency keywords trigger immediate escalation."""
        emergency_queries = [
            "I have severe chest pain and can't breathe",
            "My friend is having a heart attack right now",
            "Sudden numbness on one side of my body and slurred speech",
            "Severe bleeding and uncontrolled hemorrhage",
            "My throat is swelling up from an allergic reaction"
        ]
        for query in emergency_queries:
            res = self.bot.process_message(query)
            self.assertEqual(res["type"], "emergency", f"Failed to detect emergency in: {query}")
            self.assertTrue(res.get("emergency_flag", False))
            self.assertIn("911", res["reply"])
            self.assertIn("URGENT MEDICAL NOTICE", res["reply"])

    def test_diagnostic_and_prescription_refusal(self):
        """Verify that diagnostic or prescription inquiries are strictly refused."""
        diagnostic_queries = [
            "Can you diagnose my rash and fever?",
            "Do I have cancer or something else?",
            "What medicine should I take for this infection?",
            "Prescribe me an antibiotic for my throat",
            "What illness is this coughing symptom?"
        ]
        for query in diagnostic_queries:
            res = self.bot.process_message(query)
            self.assertEqual(res["type"], "refusal", f"Failed to refuse diagnosis/prescription for: {query}")
            self.assertIn("Medical Diagnosis & Prescription Boundary", res["reply"])
            self.assertIn("cannot diagnose", res["reply"])

    def test_educational_health_responses(self):
        """Verify that general wellness questions return educational guidance with disclaimer."""
        educational_queries = [
            "What are the best habits for sleep hygiene?",
            "How much water should I drink each day for hydration?",
            "What are the WHO recommendations for exercise?",
            "Tell me about the benefits of dietary fiber"
        ]
        for query in educational_queries:
            res = self.bot.process_message(query)
            self.assertEqual(res["type"], "educational", f"Failed educational response for: {query}")
            self.assertIn("disclaimer", res)
            self.assertIn("Educational Disclaimer", res["disclaimer"])
            self.assertTrue(len(res["reply"]) > 50)

    def test_empty_message_handling(self):
        """Verify that blank or whitespace input returns a helpful prompt."""
        res = self.bot.process_message("   ")
        self.assertEqual(res["type"], "standard")
        self.assertIn("Please feel free to ask", res["reply"])

    def test_prompt_explanation_structure(self):
        """Verify that prompt explanation data exposes role and safety guardrails."""
        info = self.bot.get_prompt_explanation()
        self.assertIn("title", info)
        self.assertIn("safety_guardrails", info)
        self.assertTrue(len(info["safety_guardrails"]) >= 3)


    def test_history_awareness(self):
        """Verify that the chatbot remembers and summarizes previous user searches."""
        # History with prior user questions
        history = [
            {"role": "user", "content": "How much water should I drink daily?"},
            {"role": "assistant", "content": "Baseline hydration recommends 2.7 to 3.7 liters daily."},
            {"role": "user", "content": "What are the best sleep hygiene tips?"}
        ]
        res = self.bot.process_message("What did I search before?", history=history)
        self.assertEqual(res["type"], "history")
        self.assertIn("How much water should I drink daily?", res["reply"])
        self.assertIn("What are the best sleep hygiene tips?", res["reply"])
        self.assertIn("disclaimer", res)

        # Empty history inquiry
        empty_res = self.bot.process_message("Show my search history", history=[])
        self.assertEqual(empty_res["type"], "history")
        self.assertIn("haven't made any previous searches", empty_res["reply"])

    def test_gemini_service_contents_formatting(self):
        """Verify that GeminiService formats multi-turn dialog into alternating roles."""
        service = self.bot.gemini_service
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help?"}
        ]
        contents = service.format_conversation_contents("Tell me about exercise", history)
        self.assertEqual(len(contents), 3)
        self.assertEqual(contents[0]["role"], "user")
        self.assertEqual(contents[0]["parts"][0]["text"], "Hello")
        self.assertEqual(contents[1]["role"], "model")
        self.assertEqual(contents[1]["parts"][0]["text"], "Hi! How can I help?")
        self.assertEqual(contents[2]["role"], "user")
        self.assertEqual(contents[2]["parts"][0]["text"], "Tell me about exercise")

    def test_chatbot_loads_env(self):
        """Verify that HealthChatbot automatically locates and loads the .env file."""
        self.assertTrue(self.bot.env_loaded, "Chatbot failed to auto-load .env file.")
        env_path = find_env_file()
        self.assertIsNotNone(env_path, "find_env_file could not locate .env")
        self.assertTrue(os.path.isfile(env_path))

    def test_chatbot_load_env_custom_file(self):
        """Verify that HealthChatbot can load and reload variables from a custom .env file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False, encoding="utf-8") as tf:
            tf.write("GOOGLE_API_KEY=custom_test_env_key_abc\n")
            tf.write("GEMINI_MODEL=gemini-1.5-pro-test\n")
            tf.write("TEST_CUSTOM_VAR=health_test_val\n")
            temp_path = tf.name

        try:
            bot = HealthChatbot(auto_load_env=False)
            self.assertFalse(bot.env_loaded)
            loaded = bot.load_env(env_path=temp_path, override=True)
            self.assertTrue(loaded)
            self.assertEqual(os.environ.get("TEST_CUSTOM_VAR"), "health_test_val")
            self.assertEqual(bot.gemini_service.api_key, "custom_test_env_key_abc")
            self.assertEqual(bot.gemini_service.model, "gemini-1.5-pro-test")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            os.environ.pop("TEST_CUSTOM_VAR", None)

    def test_builtin_env_parser(self):
        """Verify that the built-in fallback parser correctly parses comments, quotes, and exports."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False, encoding="utf-8") as tf:
            tf.write("# Comment line\n")
            tf.write("   \n")
            tf.write("PARSER_TEST_A=hello_world\n")
            tf.write('export PARSER_TEST_B="quoted value"\n')
            tf.write("PARSER_TEST_C='single quoted'\n")
            temp_path = tf.name

        try:
            success = parse_env_file(temp_path, override=True)
            self.assertTrue(success)
            self.assertEqual(os.environ.get("PARSER_TEST_A"), "hello_world")
            self.assertEqual(os.environ.get("PARSER_TEST_B"), "quoted value")
            self.assertEqual(os.environ.get("PARSER_TEST_C"), "single quoted")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            for k in ["PARSER_TEST_A", "PARSER_TEST_B", "PARSER_TEST_C"]:
                os.environ.pop(k, None)


class TestFlaskAPI(unittest.TestCase):
    """Functional tests for Flask API endpoints."""

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_home_page(self):
        """Verify that the home page serves HTML with key UI components."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")
        self.assertIn("Vitalis", content)
        self.assertIn("Prompt Explanation", content)
        self.assertIn("Health Quiz", content)
        self.assertIn("SEARCH &amp; CHAT HISTORY", content)
        self.assertIn("Google Gemini API Key", content)

    def test_health_check(self):
        """Verify that /api/health responds with healthy status."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "healthy")

    def test_chat_api(self):
        """Verify the /api/chat endpoint."""
        # Standard query
        response = self.client.post(
            "/api/chat",
            data=json.dumps({"message": "What are sleep hygiene tips?"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("reply", data)
        self.assertIn("disclaimer", data)

        # Multi-turn history awareness query
        history_response = self.client.post(
            "/api/chat",
            data=json.dumps({
                "message": "What did I ask previously?",
                "history": [
                    {"role": "user", "content": "How much fiber should I eat?"}
                ]
            }),
            content_type="application/json"
        )
        self.assertEqual(history_response.status_code, 200)
        hist_data = json.loads(history_response.data)
        self.assertEqual(hist_data["type"], "history")
        self.assertIn("How much fiber should I eat?", hist_data["reply"])

        # Empty query error handling
        bad_response = self.client.post(
            "/api/chat",
            data=json.dumps({"message": ""}),
            content_type="application/json"
        )
        self.assertEqual(bad_response.status_code, 400)

    def test_api_key_endpoints(self):
        """Verify /api/api-key/status and /api/api-key/validate endpoints."""
        # Status
        status_res = self.client.get("/api/api-key/status")
        self.assertEqual(status_res.status_code, 200)
        status_data = json.loads(status_res.data)
        self.assertIn("configured", status_data)
        self.assertIn("mode", status_data)

        # Validation with empty key
        empty_res = self.client.post(
            "/api/api-key/validate",
            data=json.dumps({"api_key": ""}),
            content_type="application/json"
        )
        self.assertEqual(empty_res.status_code, 400)

        # Validation with invalid dummy key
        val_res = self.client.post(
            "/api/api-key/validate",
            data=json.dumps({"api_key": "invalid_test_key_12345"}),
            content_type="application/json"
        )
        self.assertEqual(val_res.status_code, 200)
        val_data = json.loads(val_res.data)
        self.assertFalse(val_data["valid"])

    def test_prompt_explanation_api(self):
        """Verify the /api/prompt-explanation endpoint."""
        response = self.client.get("/api/prompt-explanation")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("safety_guardrails", data)

    def test_quiz_and_evaluation_api(self):
        """Verify the /api/quiz and /api/quiz/evaluate endpoints."""
        # GET quiz questions
        get_res = self.client.get("/api/quiz")
        self.assertEqual(get_res.status_code, 200)
        quiz_data = json.loads(get_res.data)
        self.assertGreaterEqual(quiz_data["total_questions"], 5)
        # Ensure answer_index is not exposed in GET /api/quiz
        first_q = quiz_data["questions"][0]
        self.assertNotIn("answer_index", first_q)

        # POST evaluate quiz with answers
        answers_payload = {
            "answers": {
                str(q["id"]): q["answer_index"]
                for q in QUIZ_QUESTIONS
            }
        }
        eval_res = self.client.post(
            "/api/quiz/evaluate",
            data=json.dumps(answers_payload),
            content_type="application/json"
        )
        self.assertEqual(eval_res.status_code, 200)
        eval_data = json.loads(eval_res.data)
        self.assertEqual(eval_data["score"], len(QUIZ_QUESTIONS))
        self.assertEqual(eval_data["percentage"], 100.0)


if __name__ == "__main__":
    unittest.main()
