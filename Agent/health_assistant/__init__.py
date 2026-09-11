"""
Health Assistant Package.
Exposes the core HealthChatbot class and QUIZ_QUESTIONS dataset.
"""

from .chatbot import HealthChatbot
from .quiz_data import QUIZ_QUESTIONS
from .gemini_service import GeminiService
from .env_loader import load_env, find_env_file, get_env

__all__ = [
    "HealthChatbot",
    "QUIZ_QUESTIONS",
    "GeminiService",
    "load_env",
    "find_env_file",
    "get_env"
]
