"""
Environment Variable Loader for Health Awareness Assistant.

Handles loading key-value configuration from .env files into os.environ.
Supports python-dotenv when installed and provides a robust built-in fallback parser
to ensure zero-dependency reliability in all environments.
"""

import os
from typing import Optional


def find_env_file(env_path: Optional[str] = None) -> Optional[str]:
    """
    Locate .env file from specified path, current working directory,
    or project root (parent directory of health_assistant package).
    """
    if env_path:
        abs_path = os.path.abspath(env_path)
        if os.path.isfile(abs_path):
            return abs_path
        return None

    # Search candidates in priority order
    candidates = [
        os.path.join(os.getcwd(), ".env"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".env")),
    ]

    for path in candidates:
        if os.path.isfile(path):
            return path

    return None


def parse_env_file(file_path: str, override: bool = False) -> bool:
    """
    Parse a .env file using standard library and populate os.environ.
    Handles comments, blank lines, optional 'export' prefixes, and quotes.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[7:].strip()
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key and (override or key not in os.environ):
                        os.environ[key] = val
        return True
    except Exception:
        return False


def load_env(env_path: Optional[str] = None, override: bool = False) -> bool:
    """
    Load environment variables from a .env file into os.environ.

    Attempts python-dotenv if installed, otherwise uses the built-in parser.
    Returns True if an environment file was found and processed, False otherwise.
    """
    target = find_env_file(env_path)
    if not target:
        return False

    # Attempt to load using python-dotenv if available
    try:
        import dotenv
        dotenv.load_dotenv(dotenv_path=target, override=override)
        return True
    except Exception:
        pass

    # Use built-in parser fallback
    return parse_env_file(target, override=override)


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Retrieve an environment variable value with an optional default."""
    return os.environ.get(key, default)
