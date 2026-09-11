"""
Flask Web Application for the Health Awareness Assistant.

Provides RESTful API endpoints for the educational chatbot,
interactive health awareness quiz evaluation, and system prompt explanation,
while serving the modern web frontend interface.
"""

import os
from flask import Flask, render_template, request, jsonify
from health_assistant import HealthChatbot, QUIZ_QUESTIONS, GeminiService, load_env

# Ensure .env is loaded into environment
load_env()

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# Initialize the health awareness chatbot engine
chatbot = HealthChatbot()


@app.route("/")
def index():
    """Render the primary single-page web interface."""
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify server status."""
    return jsonify({
        "status": "healthy",
        "service": "Health Awareness Assistant",
        "version": "1.1.0",
        "gemini_active": chatbot.gemini_service.has_api_key()
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Chat endpoint for health education queries.
    Enforces safety filters (emergency detection, diagnostic refusal),
    processes multi-turn search/conversation history, and generates responses
    using Google Gemini AI or evidence-informed curated knowledge base.
    """
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({
            "error": "Message cannot be empty."
        }), 400

    history = data.get("history") or []
    client_api_key = data.get("api_key") or request.headers.get("X-Google-Api-Key")

    response_data = chatbot.process_message(user_message, history=history, api_key=client_api_key)
    return jsonify(response_data)


@app.route("/api/api-key/status", methods=["GET"])
def api_key_status():
    """
    Check if Google API Key is configured on the server or in environment.
    """
    server_has_key = chatbot.gemini_service.has_api_key()
    return jsonify({
        "configured": server_has_key,
        "model": chatbot.gemini_service.model,
        "mode": "gemini" if server_has_key else "knowledge_base"
    })


@app.route("/api/api-key/validate", methods=["POST"])
def validate_api_key():
    """
    Test and validate a user-supplied Google API Key against Gemini API.
    """
    data = request.get_json(silent=True) or {}
    test_key = (data.get("api_key") or "").strip()
    if not test_key:
        return jsonify({
            "valid": False,
            "message": "API Key cannot be empty."
        }), 400

    result = chatbot.gemini_service.validate_key(test_key)
    return jsonify(result)


@app.route("/api/prompt-explanation", methods=["GET"])
def prompt_explanation():
    """
    Returns the comprehensive architectural and system prompt explanation,
    detailing the educational mission, non-clinical constraints,
    refusal policies, and emergency protocols.
    """
    explanation_data = chatbot.get_prompt_explanation()
    return jsonify(explanation_data)


@app.route("/api/quiz", methods=["GET"])
def get_quiz():
    """
    Returns the quiz questions for the frontend.
    Options and categories are provided. The correct answer is kept server-side
    until submitted for grading via /api/quiz/evaluate.
    """
    sanitized_questions = [
        {
            "id": q["id"],
            "category": q["category"],
            "question": q["question"],
            "options": q["options"]
        }
        for q in QUIZ_QUESTIONS
    ]
    return jsonify({
        "total_questions": len(sanitized_questions),
        "questions": sanitized_questions
    })


@app.route("/api/quiz/evaluate", methods=["POST"])
def evaluate_quiz():
    """
    Evaluates submitted user answers against the question bank.
    Calculates score, percentage, and returns in-depth educational feedback
    and rationales for each question.
    """
    data = request.get_json(silent=True) or {}
    user_answers = data.get("answers", {})

    total = len(QUIZ_QUESTIONS)
    correct_count = 0
    feedback = []

    for q in QUIZ_QUESTIONS:
        qid = str(q["id"])
        selected_idx = user_answers.get(qid)
        is_correct = (selected_idx is not None and int(selected_idx) == q["answer_index"])

        if is_correct:
            correct_count += 1

        feedback.append({
            "id": q["id"],
            "category": q["category"],
            "question": q["question"],
            "options": q["options"],
            "selected_index": selected_idx,
            "correct_index": q["answer_index"],
            "is_correct": is_correct,
            "explanation": q["explanation"]
        })

    percentage = round((correct_count / total) * 100, 1) if total > 0 else 0

    return jsonify({
        "score": correct_count,
        "total": total,
        "percentage": percentage,
        "feedback": feedback,
        "summary": (
            "Outstanding health literacy! Keep reinforcing these evidence-based habits."
            if percentage >= 80 else
            "Solid effort! Review the detailed rationales below to sharpen your health awareness."
            if percentage >= 50 else
            "Great opportunity for learning! Explore the explanations below and ask the chatbot any questions."
        )
    })


if __name__ == "__main__":
    # Standard development server port
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
