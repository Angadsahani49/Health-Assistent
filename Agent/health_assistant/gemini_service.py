"""
Gemini Service Module for Health Awareness Assistant.

Integrates Google's Generative Language (Gemini) API using Python standard library
(urllib.request, json) to guarantee full compatibility without external heavy dependencies.
Maintains conversational history context and enforces strict health awareness guardrails.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional


class GeminiService:
    """
    Client for interacting with Google Gemini models (e.g., gemini-1.5-flash).
    Constructs multi-turn conversational payloads, incorporates safety instructions,
    and returns sanitized educational responses.
    """

    DEFAULT_MODEL = "gemini-1.5-flash"
    API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    SYSTEM_INSTRUCTION = (
        "You are Vitalis, an empathetic, evidence-based Educational Health Awareness "
        "and Wellness Assistant. Your mission is to provide clear, accessible, and "
        "evidence-informed lifestyle education, prevention tips, and health literacy "
        "grounded in consensus from public health authorities (WHO, CDC, AHA, NIH).\n\n"
        "STRICT SAFETY GUARDRAILS (MANDATORY & NON-NEGOTIABLE):\n"
        "1. NO MEDICAL DIAGNOSIS: Never attempt to diagnose illnesses, evaluate individual symptoms "
        "as a specific condition, or guess diseases. Firmly and politely explain that an accurate "
        "clinical evaluation requires physical examination, vital signs, and diagnostic testing by a licensed physician.\n"
        "2. NO PRESCRIPTIONS OR DRUG DOSING: Never prescribe medications, suggest pharmaceutical doses, "
        "or endorse unverified medical treatments. Direct users to consult their healthcare provider or pharmacist.\n"
        "3. EMERGENCY ESCALATION: If the user describes an acute medical emergency (severe chest pain, "
        "shortness of breath, stroke signs, severe hemorrhage, poisoning, or crisis/self-harm), immediately "
        "instruct them to call 911 (or local emergency services) or visit the nearest emergency department without delay.\n"
        "4. EDUCATIONAL DISCLAIMER: Always frame responses as general educational information, not medical advice.\n"
        "5. HISTORY AWARENESS: You have access to the user's previous questions, searches, and conversational context. "
        "Refer back to what they asked or searched for previously when relevant to provide cohesive, personalized guidance."
    )

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        if not api_key and not os.environ.get("GOOGLE_API_KEY") and not os.environ.get("GEMINI_API_KEY"):
            try:
                from .env_loader import load_env
            except (ImportError, ValueError):
                import sys
                sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
                from health_assistant.env_loader import load_env
            load_env()

        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or ""
        self.model = model or os.environ.get("GEMINI_MODEL", self.DEFAULT_MODEL)

    def set_api_key(self, api_key: str):
        """Update active API key."""
        self.api_key = api_key.strip()

    def has_api_key(self, custom_key: Optional[str] = None) -> bool:
        """Check if an API key is available."""
        key = (custom_key or self.api_key or "").strip()
        return bool(key)

    def validate_key(self, custom_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate an API key by making a lightweight test request to the Gemini API.
        Returns a dict with 'valid' (bool) and 'message' (str).
        """
        key = (custom_key or self.api_key or "").strip()
        if not key:
            return {"valid": False, "message": "API key is empty."}

        url = f"{self.API_BASE_URL}/{self.model}:generateContent?key={key}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": "Health assistant ping"}]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 10
            }
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return {"valid": True, "message": "Google Gemini API key verified successfully."}
                return {"valid": False, "message": f"Server responded with status {response.status}."}
        except urllib.error.HTTPError as e:
            try:
                err_body = json.loads(e.read().decode("utf-8"))
                msg = err_body.get("error", {}).get("message", str(e))
            except Exception:
                msg = str(e)
            return {"valid": False, "message": f"API Error ({e.code}): {msg}"}
        except urllib.error.URLError as e:
            return {"valid": False, "message": f"Network Error: {e.reason}"}
        except Exception as e:
            return {"valid": False, "message": f"Unexpected Error: {str(e)}"}

    def format_conversation_contents(
        self,
        current_message: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Format multi-turn conversation history into Gemini's contents format.
        history expects a list of dicts: [{'role': 'user'|'assistant'|'model', 'content': '...'}]
        """
        contents: List[Dict[str, Any]] = []

        if history:
            # Take up to last 10 turns to stay within comfortable token budgets
            for turn in history[-10:]:
                role = turn.get("role", "user")
                text = turn.get("content", "").strip()
                if not text:
                    continue

                # Map 'assistant' role to Gemini's 'model' role
                gemini_role = "model" if role in ("assistant", "model") else "user"
                
                # Gemini expects alternating roles; prevent consecutive identical roles
                if contents and contents[-1]["role"] == gemini_role:
                    # Append text to existing part
                    contents[-1]["parts"][0]["text"] += f"\n\n{text}"
                else:
                    contents.append({
                        "role": gemini_role,
                        "parts": [{"text": text}]
                    })

        # Ensure the current message is added as the last user prompt
        if contents and contents[-1]["role"] == "user":
            contents[-1]["parts"][0]["text"] += f"\n\n{current_message}"
        else:
            contents.append({
                "role": "user",
                "parts": [{"text": current_message}]
            })

        return contents

    def generate_response(
        self,
        user_message: str,
        history: Optional[List[Dict[str, str]]] = None,
        custom_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate educational health response from Google Gemini API with conversational history.
        """
        key = (custom_key or self.api_key or "").strip()
        if not key:
            raise ValueError("No Google API Key provided.")

        url = f"{self.API_BASE_URL}/{self.model}:generateContent?key={key}"
        contents = self.format_conversation_contents(user_message, history)

        payload = {
            "systemInstruction": {
                "parts": [{"text": self.SYSTEM_INSTRUCTION}]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.9,
                "maxOutputTokens": 1024
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=18) as response:
            result = json.loads(response.read().decode("utf-8"))

        candidates = result.get("candidates", [])
        if not candidates:
            raise ValueError("Gemini API returned no candidates.")

        candidate = candidates[0]
        content_parts = candidate.get("content", {}).get("parts", [])
        if not content_parts:
            raise ValueError("Gemini candidate contains no content parts.")

        reply_text = "".join(part.get("text", "") for part in content_parts).strip()

        # Extract suggested follow-up chips based on topics mentioned
        suggested_topics = self._derive_suggestions(reply_text)

        return {
            "reply": reply_text,
            "type": "educational",
            "source": "gemini",
            "model": self.model,
            "suggested_topics": suggested_topics
        }

    def _derive_suggestions(self, text: str) -> List[str]:
        """Generate contextual suggestion chips from response content."""
        lower = text.lower()
        suggestions = []

        if "sleep" in lower:
            suggestions.append("Sleep hygiene habits")
        if "water" in lower or "hydration" in lower:
            suggestions.append("Hydration guidelines")
        if "exercise" in lower or "activity" in lower or "walking" in lower:
            suggestions.append("WHO physical activity guidelines")
        if "diet" in lower or "nutrition" in lower or "fiber" in lower:
            suggestions.append("Balanced nutrition basics")
        if "stress" in lower or "breathing" in lower:
            suggestions.append("Diaphragmatic breathing")
        if "heart" in lower or "blood pressure" in lower:
            suggestions.append("Cardiovascular wellness")

        # Fallback suggestions if none detected
        if len(suggestions) < 3:
            default_pool = [
                "Sleep hygiene tips",
                "Daily hydration markers",
                "Balanced plate guidelines",
                "Stress resilience techniques",
                "Take the Health Quiz"
            ]
            for s in default_pool:
                if s not in suggestions:
                    suggestions.append(s)
                if len(suggestions) >= 4:
                    break

        return suggestions[:4]
