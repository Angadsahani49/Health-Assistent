"""
Health Awareness Assistant Core Engine.

This module implements the core conversational logic, intent routing,
strict medical safety guardrails, emergency detection protocols,
and health education knowledge base.
"""

import os
import re
from typing import Dict, Any, List, Optional
try:
    from .gemini_service import GeminiService
    from .env_loader import load_env, find_env_file, get_env
except (ImportError, ValueError):
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from health_assistant.gemini_service import GeminiService
    from health_assistant.env_loader import load_env, find_env_file, get_env


class HealthChatbot:
    """
    Health Awareness Assistant Chatbot.
    Enforces strict safety boundaries, refuses diagnostic/prescriptive queries,
    detects medical emergencies, and provides evidence-informed health education.
    """

    DISCLAIMER = (
        "Educational Disclaimer: This assistant provides general health awareness "
        "and educational information only. It is not a substitute for professional "
        "medical advice, diagnosis, or treatment. Always consult a qualified healthcare "
        "professional for personalized medical guidance or concerning symptoms."
    )

    EMERGENCY_BANNER = (
        "🚨 URGENT MEDICAL NOTICE: If you or someone around you is experiencing a medical "
        "emergency, severe chest pain, shortness of breath, sudden weakness or numbness, "
        "severe bleeding, or thoughts of self-harm, please call 911 (or your local emergency "
        "dispatch number) or visit the nearest emergency department immediately. "
        "This assistant cannot provide emergency medical intervention or triage."
    )

    SYSTEM_PROMPT_DETAILS = {
        "title": "Health Awareness Assistant System Architecture & Prompt Design",
        "role": "Educational Health & Wellness Companion",
        "core_mission": (
            "Empower users with evidence-based health awareness, lifestyle prevention tips, "
            "and wellness literacy while upholding uncompromising medical safety standards."
        ),
        "safety_guardrails": [
            {
                "rule": "Strict No-Diagnosis Policy",
                "description": (
                    "The assistant will never attempt to diagnose medical conditions, analyze individual "
                    "symptoms for pathology, or guess diseases from user reports. Diagnostic queries are "
                    "firmly redirected to licensed clinicians."
                )
            },
            {
                "rule": "Zero Prescription & Treatment Claims",
                "description": (
                    "The assistant strictly avoids prescribing drugs, recommending dosage adjustments, "
                    "or claiming unverified home cures. It clarifies that medication regimens must be "
                    "managed by an authorized healthcare provider."
                )
            },
            {
                "rule": "Proactive Emergency Escalation",
                "description": (
                    "Automated pattern matching intercepts life-threatening keywords (e.g. chest agony, "
                    "stroke indicators, anaphylaxis, severe respiratory distress) and displays prominent "
                    "emergency hotline escalation guidance without delay."
                )
            },
            {
                "rule": "Mandatory Universal Disclaimer",
                "description": (
                    "Every educational output is framed with clear educational disclaimers reminding "
                    "users that AI output is for educational literacy only."
                )
            },
            {
                "rule": "Evidence-Informed Educational Guidance",
                "description": (
                    "Responses are grounded in recommendations from public health organizations such as "
                    "the World Health Organization (WHO), CDC, AHA, and National Institutes of Health (NIH)."
                )
            }
        ],
        "interaction_guidelines": [
            "Maintain an empathetic, supportive, yet strictly non-clinical educational tone.",
            "Break down complex health concepts (e.g., blood pressure, glycemic index, circadian rhythm) into approachable language.",
            "Promote proactive habits: balanced nutrition, restorative sleep, regular movement, stress resilience, and routine preventative screenings.",
            "Provide transparent insight into system operations via the Prompt Explanation interface."
        ]
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        env_path: Optional[str] = None,
        auto_load_env: bool = True
    ):
        self.env_loaded = False
        if auto_load_env:
            self.env_loaded = self.load_env(env_path=env_path)
        self.gemini_service = GeminiService(api_key=api_key)
        self._compile_patterns()

    def load_env(self, env_path: Optional[str] = None, override: bool = False) -> bool:
        """
        Load or reload configuration from a .env file into os.environ and GeminiService.
        Returns True if a .env file was successfully found and parsed.
        """
        loaded = load_env(env_path=env_path, override=override)
        self.env_loaded = loaded
        if hasattr(self, "gemini_service") and self.gemini_service:
            # Propagate updated API key and model if available
            env_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
            if env_key and (override or not self.gemini_service.api_key):
                self.gemini_service.set_api_key(env_key)
            env_model = os.environ.get("GEMINI_MODEL")
            if env_model and (override or not self.gemini_service.model):
                self.gemini_service.model = env_model
        return loaded

    def _compile_patterns(self):
        """Compile regex patterns for emergency detection, diagnosis requests, history queries, and topic matching."""
        # Emergency red-flag symptoms
        self.emergency_patterns = [
            r"\b(chest\s+(?:pain|pressure|tightness|heaviness)|heart\s+attack|crushing\s+chest)\b",
            r"\b(can['’]?t\s+breathe|cannot\s+breathe|short(?:ness)?\s+of\s+breath|difficulty\s+breathing|asphyxiat|choking)\b",
            r"\b(stroke|face\s+droop|slurred\s+speech|sudden\s+numbness|arm\s+weakness)\b",
            r"\b(severe\s+bleeding|uncontrolled\s+hemorrhage|coughing\s+blood|vomiting\s+blood)\b",
            r"\b(anaphylaxis|allergic\s+reaction|throat.*swell|swell.*throat)\b",
            r"\b(suicid|kill\s+myself|end\s+my\s+life|self[\s-]harm|overdose)\b",
            r"\b(unconscious|passed\s+out|loss\s+of\s+consciousness|seizure\s+now|convulsion)\b"
        ]

        # Diagnostic & prescriptive solicitation triggers
        self.diagnostic_patterns = [
            r"\b(diagnose|do\s+i\s+have|could\s+i\s+have|what\s+disease|what\s+illness\s+is\s+this)\b",
            r"\b(what\s+is\s+wrong\s+with\s+me|tell\s+me\s+my\s+diagnosis|am\s+i\s+sick\s+with)\b",
            r"\b(what\s+medicine\s+should\s+i\s+take|what\s+drug|prescribe|give\s+me\s+a\s+prescription)\b",
            r"\b(how\s+much\s+(mg|milligram|dosage|dose)\s+of\s+[a-z]+)\b",
            r"\b(is\s+this\s+(cancer|tumor|infection|covid|diabetes|melanoma))\b",
            r"\b(look\s+at\s+my\s+rash|examine\s+my\s+symptom|interpret\s+my\s+blood\s+test|lab\s+results\s+show)\b"
        ]

        # History and previous searches query patterns
        self.history_patterns = [
            r"\b(what\s+did\s+i\s+(?:ask|search|say)|previous\s+(?:searches|search|questions|queries|chat)|my\s+search\s+history|search\s+history|what\s+was\s+my\s+last\s+(?:question|search)|what\s+have\s+we\s+talked\s+about)\b"
        ]

        # General health topic keyword matchers
        self.topic_matchers = {
            "hydration": [r"\b(hydrat|water|drink\s+water|fluid\s+intake|dehydrat)\b"],
            "sleep": [r"\b(sleep|insomnia|rest|bedtime|circadian|melatonin|wake\s+up)\b"],
            "nutrition": [r"\b(diet|nutrition|food|eating|eat|fiber|protein|carbs|vegetable|fruit|sugar|calorie)\b"],
            "exercise": [r"\b(exercise|workout|physical\s+activity|cardio|walking|running|gym|fitness|strength\s+training)\b"],
            "stress": [r"\b(stress|anxiety|mental\s+health|calm|relax|meditat|mindful|burnout|breath)\b"],
            "heart": [r"\b(heart\s+health|blood\s+pressure|hypertension|cholesterol|cardiovascular)\b"],
            "skin": [r"\b(sunscreen|uv|skin\s+care|sun\s+protect|sunburn|spf)\b"],
            "prevention": [r"\b(prevention|preventive|screening|vaccin|checkup|annual\s+exam|hygiene|wash\s+hands)\b"],
            "quiz_inquiry": [r"\b(quiz|test\s+my\s+knowledge|health\s+trivia|question)\b"],
            "prompt_inquiry": [r"\b(how\s+do\s+you\s+work|prompt|system\s+prompt|guardrails|who\s+are\s+you|rules)\b"]
        }

    def detect_emergency(self, text: str) -> bool:
        """Evaluate if the user input implies an active medical emergency."""
        text_lower = text.lower()
        return any(re.search(pat, text_lower) for pat in self.emergency_patterns)

    def detect_diagnostic_request(self, text: str) -> bool:
        """Evaluate if the user query solicits diagnostic evaluation or prescriptions."""
        text_lower = text.lower()
        return any(re.search(pat, text_lower) for pat in self.diagnostic_patterns)

    def _is_history_query(self, text: str) -> bool:
        """Check if the user is inquiring about their previous searches/questions."""
        text_lower = text.lower()
        return any(re.search(pat, text_lower) for pat in self.history_patterns)

    def _get_history_summary(self, history: Optional[List[Dict[str, str]]]) -> Optional[Dict[str, Any]]:
        """Summarize previous user searches and questions from conversation history."""
        if not history:
            return {
                "reply": (
                    "📜 **Search & Conversation History**\n\n"
                    "You haven't made any previous searches or asked questions in this session yet! "
                    "Feel free to ask about hydration, sleep hygiene, nutrition, physical activity, or stress management."
                ),
                "type": "history",
                "disclaimer": self.DISCLAIMER,
                "suggested_topics": ["Hydration tips", "Sleep hygiene habits", "WHO exercise guidelines", "Take the Health Quiz"]
            }

        user_queries = [
            turn.get("content", "").strip()
            for turn in history
            if turn.get("role") == "user" and turn.get("content", "").strip()
        ]

        if not user_queries:
            return {
                "reply": (
                    "📜 **Search & Conversation History**\n\n"
                    "No previous user questions recorded in this session yet. What would you like to learn about today?"
                ),
                "type": "history",
                "disclaimer": self.DISCLAIMER,
                "suggested_topics": ["Hydration tips", "Sleep hygiene", "Balanced diet", "Take the Health Quiz"]
            }

        formatted_list = "\n".join([f"{i+1}. *\"{q}\"*" for i, q in enumerate(user_queries)])
        return {
            "reply": (
                f"📜 **Your Previous Searches & Questions ({len(user_queries)} in this session):**\n\n"
                f"{formatted_list}\n\n"
                "I remember all your previous questions and searches! You can ask me to expand on any of these topics, "
                "compare recommendations, or explore new wellness practices."
            ),
            "type": "history",
            "disclaimer": self.DISCLAIMER,
            "suggested_topics": user_queries[-2:] if len(user_queries) >= 2 else ["Sleep hygiene", "Hydration tips", "Take the Health Quiz"]
        }

    def get_prompt_explanation(self) -> Dict[str, Any]:
        """Return the architectural and prompt explanation data for the UI."""
        return self.SYSTEM_PROMPT_DETAILS

    def process_message(
        self,
        user_text: str,
        history: Optional[List[Dict[str, str]]] = None,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main processing pipeline for incoming messages:
        1. Validate non-empty input
        2. Emergency triage screening (Highest Priority)
        3. Diagnostic/prescriptive boundary enforcement
        4. Google Gemini API generation with multi-turn history (if API key available)
        5. Search & Conversation history query inspection (fallback / offline mode)
        6. Curated educational knowledge base matching
        """
        cleaned = user_text.strip()
        if not cleaned:
            return {
                "reply": "Please feel free to ask an educational health question, such as tips for better sleep, balanced nutrition, daily physical activity, or stress resilience.",
                "type": "standard",
                "disclaimer": self.DISCLAIMER,
                "suggested_topics": ["Hydration tips", "Sleep hygiene", "Physical activity guidelines", "Stress management"]
            }

        # Step 1: Emergency check (Highest Priority)
        if self.detect_emergency(cleaned):
            return {
                "reply": (
                    f"{self.EMERGENCY_BANNER}\n\n"
                    "**Why this response is triggered:** Your query mentions symptoms or situations that may require "
                    "immediate emergency medical evaluation. As an AI health awareness assistant, I am not equipped to assess "
                    "acute symptoms, perform triage, or guide emergency care. Please contact emergency services right away."
                ),
                "type": "emergency",
                "disclaimer": self.DISCLAIMER,
                "emergency_flag": True,
                "suggested_topics": ["Call 911 / Local Emergency", "Poison Control (1-800-222-1222)", "Crisis Lifeline (988)"]
            }

        # Step 2: Diagnostic & Prescription refusal check
        if self.detect_diagnostic_request(cleaned):
            return {
                "reply": (
                    "**Safety Notice: Medical Diagnosis & Prescription Boundary**\n\n"
                    "I cannot diagnose medical conditions, interpret individual symptoms, suggest medications, "
                    "or provide clinical treatment plans.\n\n"
                    "**Why this boundary exists:**\n"
                    "• Accurate diagnosis requires a comprehensive physical examination, vital signs, validated lab testing, and individualized medical history review by a licensed practitioner.\n"
                    "• AI models cannot replace clinical diagnostic judgment, and guessing health conditions can delay vital clinical care.\n\n"
                    "**What you can do:**\n"
                    "• If you have persistent, new, or worrying symptoms, please book an appointment with a primary care physician or appropriate medical clinic.\n"
                    "• In the meantime, I am happy to share **general educational information** regarding preventive health habits, nutrition fundamentals, sleep hygiene, or how the human body generally functions."
                ),
                "type": "refusal",
                "disclaimer": self.DISCLAIMER,
                "suggested_topics": [
                    "What are general sleep hygiene tips?",
                    "How much water should I drink daily?",
                    "WHO guidelines for physical exercise",
                    "How does dietary fiber benefit health?"
                ]
            }

        # Step 3: Search & Conversation History query handling (always checked before API call
        # so history lookups are never routed through Gemini and never consume API quota)
        if self._is_history_query(cleaned):
            history_summary = self._get_history_summary(history)
            if history_summary:
                return history_summary

        # Step 4: Google Gemini API Generation (when API key is configured or provided)
        if self.gemini_service.has_api_key(api_key):
            try:
                gemini_res = self.gemini_service.generate_response(cleaned, history=history, custom_key=api_key)
                gemini_res["disclaimer"] = self.DISCLAIMER
                return gemini_res
            except Exception as e:
                # Log or capture error and fallback gracefully to curated knowledge base
                pass

        # Step 5: Curated Knowledge retrieval & Educational matching
        topic = self._classify_topic(cleaned)
        educational_response = self._get_educational_content(topic, cleaned)

        return {
            "reply": educational_response["content"],
            "type": educational_response.get("type", "educational"),
            "topic": topic,
            "source": "knowledge_base",
            "disclaimer": self.DISCLAIMER,
            "suggested_topics": educational_response.get("suggestions", [
                "Sleep hygiene tips",
                "Balanced plate guidelines",
                "Cardiovascular health tips",
                "Stress-reduction techniques"
            ])
        }

    def _classify_topic(self, text: str) -> Optional[str]:
        """Match query text against educational topic keywords."""
        text_lower = text.lower()
        for topic, patterns in self.topic_matchers.items():
            if any(re.search(pat, text_lower) for pat in patterns):
                return topic
        return None

    def _get_educational_content(self, topic: Optional[str], original_text: str) -> Dict[str, Any]:
        """Return curated, evidence-based educational insights for matched topics."""
        lower = original_text.lower()

        # Greetings or introductory inquiries
        if any(greet in lower for greet in ["hello", "hi", "hey", "good morning", "good evening", "greetings"]):
            return {
                "type": "greeting",
                "content": (
                    "👋 **Hello! Welcome to the Health Awareness Assistant.**\n\n"
                    "I am an educational chatbot designed to help you explore healthy-lifestyle practices, "
                    "evidence-based preventive habits, and general wellness literacy.\n\n"
                    "**Explore topics like:**\n"
                    "💧 **Hydration:** Daily fluid needs & hydration markers\n"
                    "😴 **Sleep Hygiene:** Habits for deeper, more restorative rest\n"
                    "🥗 **Nutrition:** Whole foods, dietary fiber, and balanced eating\n"
                    "🏃 **Physical Activity:** WHO guidelines for cardiovascular and muscular fitness\n"
                    "🧘 **Stress Resilience:** Diaphragmatic breathing and mindfulness fundamentals\n\n"
                    "💡 *Tip:* Check out the **'Prompt Explanation'** button in the sidebar to inspect my safety architecture, "
                    "or test your preventive literacy with the **'Quiz'** button!"
                ),
                "suggestions": ["Hydration guidelines", "Sleep hygiene habits", "WHO exercise guidelines", "Take the Health Quiz"]
            }

        if topic == "prompt_inquiry":
            return {
                "type": "meta",
                "content": (
                    "🔍 **How I Work (System Prompt & Operational Architecture)**\n\n"
                    "I operate under a carefully engineered prompt architecture centered on **educational empowerment** "
                    "and **strict clinical safety boundaries**:\n\n"
                    "1. **Non-Clinical Role:** My instructions strictly restrict me from acting as a clinician. I provide health literacy and preventive lifestyle concepts only.\n"
                    "2. **Pre-Response Filtering:** Inbound messages are evaluated for life-threatening emergency cues (immediate 911 escalation) and diagnostic solicitations (firm, polite redirection).\n"
                    "3. **Public Health Consensus:** Informational responses mirror consensus guidelines from the WHO, CDC, AHA, and NIH.\n"
                    "4. **Full Transparency:** You can click the **'Prompt Explanation'** button in the sidebar at any time to read a comprehensive breakdown of the system prompt and safety policies."
                ),
                "suggestions": ["View Prompt Explanation", "Take the Health Quiz", "How much water should I drink?", "Sleep hygiene checklist"]
            }

        if topic == "quiz_inquiry":
            return {
                "type": "quiz_referral",
                "content": (
                    "🧠 **Health Awareness Quiz Available!**\n\n"
                    "Ready to challenge your knowledge on hydration, sleep, exercise, and preventive health? "
                    "Click the **'Quiz'** button in the left sidebar to start the interactive quiz with instant answer feedback and detailed rationales!"
                ),
                "suggestions": ["Start Quiz", "Nutrition fundamentals", "Sleep habits", "Physical activity guidelines"]
            }

        if topic == "hydration":
            return {
                "type": "educational",
                "content": (
                    "💧 **Health Education: Daily Hydration Guidelines**\n\n"
                    "Adequate hydration is critical for thermoregulation, nutrient transportation, joint lubrication, "
                    "and cognitive clarity.\n\n"
                    "**Key Preventive Health Insights:**\n"
                    "• **Fluid Baseline:** While individual requirements vary based on body size, climate, and activity, the U.S. National Academies suggest an average daily fluid intake of ~3.7 liters (15.5 cups) for adult men and ~2.7 liters (11.5 cups) for adult women (from all beverages and moisture-rich foods).\n"
                    "• **Urine Color Indicator:** Pale straw or light transparent yellow indicates healthy hydration. Dark amber urine signifies concentrated fluids and signals the need to drink water.\n"
                    "• **Beyond Plain Water:** Unsweetened herbal teas, water-rich vegetables (cucumbers, celery), and fresh fruits contribute effectively to daily fluid quotas.\n"
                    "• **Electrolyte Balance:** During prolonged vigorous exercise or hot climates, balancing water with essential electrolytes (sodium, potassium, magnesium) helps prevent hyponatremia."
                ),
                "suggestions": ["Signs of dehydration", "Sleep hygiene tips", "Physical activity recommendations", "Take the Health Quiz"]
            }

        if topic == "sleep":
            return {
                "type": "educational",
                "content": (
                    "😴 **Health Education: Sleep Hygiene & Circadian Rhythm**\n\n"
                    "Restorative sleep is foundational for immunological resilience, memory consolidation, "
                    "cardiovascular recovery, and hormonal equilibrium.\n\n"
                    "**Evidence-Based Sleep Hygiene Practices:**\n"
                    "• **Consistency:** Keep a consistent sleep and wake schedule seven days a week, anchoring your internal master circadian clock.\n"
                    "• **Light Management:** Maximize natural outdoor morning sunlight exposure within an hour of waking to reinforce daytime cortisol and nighttime melatonin production. Dim household lights and minimize blue-light screens 60–90 minutes before bed.\n"
                    "• **Bedroom Environment:** Maintain a cool, quiet, and dark sleeping sanctuary (optimal ambient sleep temperature is typically between 65°F–68°F / 18°C–20°C).\n"
                    "• **Caffeine Timing:** Avoid caffeinated beverages 6 to 8 hours before planned sleep, as caffeine's half-life can disrupt deep slow-wave sleep stages."
                ),
                "suggestions": ["Stress reduction techniques", "Physical activity tips", "Nutrition for energy", "Take the Health Quiz"]
            }

        if topic == "nutrition":
            return {
                "type": "educational",
                "content": (
                    "🥗 **Health Education: Nutrition & Balanced Eating Principles**\n\n"
                    "A nutrient-dense eating pattern fosters cellular repair, sustains steady metabolic energy, "
                    "and drastically reduces long-term risks of chronic lifestyle illnesses.\n\n"
                    "**Core Nutritional Foundations:**\n"
                    "• **The Balanced Plate Model:** Aim to fill half your plate with colorful non-starchy vegetables and whole fruits, one quarter with quality proteins (beans, lentils, fish, poultry, tofu), and one quarter with complex whole grains (quinoa, brown rice, oats).\n"
                    "• **Dietary Fiber Power:** Adults should target 25 to 38 grams of fiber daily. Soluble fiber (oats, legumes, apples) aids cholesterol and glycemic control, while insoluble fiber promotes healthy intestinal transit.\n"
                    "• **Healthy Fats:** Emphasize monounsaturated and polyunsaturated fats from extra virgin olive oil, avocados, nuts, seeds, and omega-3 fatty acids from wild fish or flaxseed.\n"
                    "• **Limit Ultra-Processed Items:** Minimize foods high in added refined sugars, industrial trans fats, and excess sodium to protect vascular endothelial health."
                ),
                "suggestions": ["Benefits of dietary fiber", "Hydration guidelines", "Cardiovascular health", "Take the Health Quiz"]
            }

        if topic == "exercise":
            return {
                "type": "educational",
                "content": (
                    "🏃 **Health Education: Physical Activity & Movement Guidelines**\n\n"
                    "Regular physical activity is one of the most impactful lifestyle interventions for cardiovascular health, "
                    "metabolic regulation, bone density, and emotional well-being.\n\n"
                    "**World Health Organization (WHO) Adult Guidelines:**\n"
                    "• **Aerobic Activity:** At least **150–300 minutes** of moderate-intensity aerobic physical activity (e.g., brisk walking, cycling, leisurely swimming) or **75–150 minutes** of vigorous-intensity aerobic physical activity (e.g., running, interval training) weekly.\n"
                    "• **Strength Training:** Incorporate muscle-strengthening activities that involve all major muscle groups on **2 or more days** each week.\n"
                    "• **Break Sedentary Time:** Sitting for unbroken stretches slows metabolic clearance of fats and glucose. Stand, stretch, or walk for 2 minutes every 30–60 minutes."
                ),
                "suggestions": ["Exercise tips for beginners", "Sleep hygiene", "Stress relief breathing", "Take the Health Quiz"]
            }

        if topic == "stress":
            return {
                "type": "educational",
                "content": (
                    "🧘 **Health Education: Stress Resilience & Nervous System Balance**\n\n"
                    "Chronic psychological stress causes sustained elevation of cortisol and sympathetic tone, "
                    "which can impact immunity, digestion, sleep quality, and cardiovascular stability.\n\n"
                    "**Evidence-Based De-Stressing Techniques:**\n"
                    "• **Diaphragmatic 'Belly' Breathing:** Engage slow, deep breaths where the exhalation is longer than the inhalation (e.g., inhale for 4 seconds, exhale smoothly for 6 seconds). This stimulates the vagus nerve and activates the parasympathetic 'rest-and-digest' branch.\n"
                    "• **Box Breathing (4-4-4-4):** Inhale 4s, hold 4s, exhale 4s, hold 4s. Used widely to down-regulate acute performance anxiety.\n"
                    "• **Nature Exposure & Movement:** Even a 20-minute walk in natural surroundings ('green exercise') lowers salivary cortisol levels.\n"
                    "• **Boundaries & Social Connection:** Cultivating meaningful relationships and establishing healthy digital/work boundaries protects emotional bandwidth."
                ),
                "suggestions": ["Sleep hygiene tips", "Physical activity for mood", "Hydration guidelines", "Take the Health Quiz"]
            }

        if topic == "heart":
            return {
                "type": "educational",
                "content": (
                    "❤️ **Health Education: Cardiovascular Health & Blood Pressure Basics**\n\n"
                    "Your heart pumps approximately 2,000 gallons of blood daily through 60,000 miles of blood vessels.\n\n"
                    "**Understanding the Numbers:**\n"
                    "• **Normal Blood Pressure:** Systolic under 120 mm Hg AND Diastolic under 80 mm Hg (<120/<80 mm Hg).\n"
                    "• **Lifestyle Heart Protectors:**\n"
                    "  - Regular aerobic exercise (strengthens myocardial efficiency)\n"
                    "  - DASH diet pattern (rich in potassium, magnesium, calcium from vegetables, nuts, and low-fat dairy with restricted sodium)\n"
                    "  - Avoiding tobacco and excessive alcohol\n"
                    "  - Maintaining healthy restorative sleep (consistently sleeping <6 hours is correlated with heightened hypertension risk)\n\n"
                    "*(Note: Blood pressure targets should always be personalized with your clinical provider.)*"
                ),
                "suggestions": ["WHO physical activity guidelines", "Nutrition for heart health", "Stress management", "Take the Health Quiz"]
            }

        if topic == "skin":
            return {
                "type": "educational",
                "content": (
                    "☀️ **Health Education: Sun Safety & Ultraviolet (UV) Protection**\n\n"
                    "Ultraviolet radiation from sunlight accounts for up to 90% of preventable premature skin aging and skin cancers.\n\n"
                    "**Dermatological Prevention Guidelines:**\n"
                    "• **Broad-Spectrum SPF 30+:** Use broad-spectrum sunscreen (protecting against both UVA aging rays and UVB burning rays) with an SPF of at least 30.\n"
                    "• **Application & Reapplication:** Apply roughly one ounce (a shot-glass amount) to exposed areas 15–30 minutes before stepping outdoors. Reapply at least every 2 hours, or immediately after swimming or heavy perspiration.\n"
                    "• **Peak UV Avoidance:** UV rays are most intense between 10 a.m. and 4 p.m. Seek shade and wear UV-rated sunglasses and wide-brimmed hats when outside."
                ),
                "suggestions": ["Hydration tips", "Preventive checkups", "General wellness habits", "Take the Health Quiz"]
            }

        if topic == "prevention":
            return {
                "type": "educational",
                "content": (
                    "🛡️ **Health Education: Preventive Health & Routine Screenings**\n\n"
                    "Preventive healthcare prioritizes stopping diseases before they start or catching them in early, highly manageable stages.\n\n"
                    "**Cornerstones of Prevention:**\n"
                    "• **Annual Well-Woman / Well-Man Visits:** Routine checks for blood pressure, blood glucose, lipid panels, and skin checks.\n"
                    "• **Hand Hygiene:** Washing hands with soap and water for at least 20 seconds remains one of the simplest, most effective defenses against viral and bacterial transmission.\n"
                    "• **Immunizations:** Staying current with evidence-backed vaccinations protects not only the individual but prevents community-wide transmission to vulnerable populations.\n"
                    "• **Dental & Vision Exams:** Oral health is deeply linked to systemic inflammatory load and cardiovascular health."
                ),
                "suggestions": ["Nutrition principles", "Sleep hygiene", "Cardiovascular basics", "Take the Health Quiz"]
            }

        # Fallback general educational response
        return {
            "type": "educational",
            "content": (
                "📚 **General Health Awareness & Prevention**\n\n"
                f"Thank you for your question: *\"{original_text}\"*\n\n"
                "As an educational assistant, I focus on evidence-based lifestyle habits and preventive health literacy. "
                "The pillars of long-term vitality include:\n\n"
                "1. **Restorative Sleep:** 7–9 hours of consistent, dark, quiet rest.\n"
                "2. **Balanced Nutrition:** Diverse whole foods, ample dietary fiber, and adequate hydration.\n"
                "3. **Daily Movement:** At least 150 minutes of moderate activity weekly plus strength training.\n"
                "4. **Stress Resilience:** Mindful breathing, social connection, and regular outdoor breaks.\n"
                "5. **Routine Preventive Care:** Regular physical checkups and age-appropriate screenings.\n\n"
                "Feel free to ask for specific tips on any of these wellness areas, or click **'Prompt Explanation'** or **'Quiz'** in the sidebar!"
            ),
            "suggestions": [
                "Hydration guidelines",
                "Sleep hygiene tips",
                "Physical activity guidelines",
                "Stress-reduction techniques"
            ]
        }


if __name__ == "__main__":
    import io
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "buffer"):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    print("=" * 65)
    print("🌿 Vitalis: Health Awareness Assistant - Interactive Chatbot")
    print("=" * 65)

    bot = HealthChatbot()
    env_file = find_env_file()

    print(f"📁 .env configuration file : {env_file if env_file else 'None found'}")
    if bot.gemini_service.has_api_key():
        print(f"✨ Gemini API Mode         : Active (Model: {bot.gemini_service.model})")
    else:
        print("💡 Knowledge Base Mode     : Active (Curated offline health insights)")

    print(f"\n{bot.DISCLAIMER}\n")
    print("Ask any health question (type 'quit' to exit, 'history' to view previous queries):\n")

    chat_history: List[Dict[str, str]] = []
    while True:
        try:
            prompt = input("You > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Stay well!")
            break

        if not prompt:
            continue
        if prompt.lower() in ("quit", "exit", "q"):
            print("Goodbye! Take care.")
            break

        response = bot.process_message(prompt, history=chat_history)
        print(f"\nVitalis >\n{response.get('reply')}\n")

        chips = response.get("suggested_topics")
        if chips:
            print(f"💡 Suggested follow-ups: {', '.join(chips)}\n")

        chat_history.append({"role": "user", "content": prompt})
        chat_history.append({"role": "assistant", "content": response.get("reply", "")})
