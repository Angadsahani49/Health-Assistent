"""
Hello Gemini - Test Script for Google Gemini API.

Loads the API key and model configuration from .env and performs a test API call
to Google Gemini using standard library urllib.request (zero external dependencies required).
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error

# Ensure stdout and stderr handle UTF-8 safely on Windows command consoles
if hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    import io
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Load environment configuration (.env)
try:
    from health_assistant import load_env, find_env_file
    load_env()
except Exception:
    # Direct standalone fallback loader if executed in isolation
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.isfile(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v


def call_gemini(
    prompt: str,
    api_key: str,
    model: str = "gemini-1.5-flash"
) -> dict:
    """
    Make an API call to Google Generative Language API (Gemini).

    Args:
        prompt: Text message to send to Gemini.
        api_key: Google AI Studio API Key.
        model: Model name (e.g., 'gemini-1.5-flash', 'gemini-2.0-flash').

    Returns:
        dict: {'success': bool, 'text': str, 'raw': dict, 'error': str, 'status_code': int}
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            status_code = resp.status
            body = json.loads(resp.read().decode("utf-8"))

        candidates = body.get("candidates", [])
        if not candidates:
            return {
                "success": False,
                "error": "Gemini API returned an empty candidates list.",
                "status_code": status_code,
                "raw": body
            }

        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts).strip()

        return {
            "success": True,
            "text": text,
            "model": model,
            "status_code": status_code,
            "raw": body
        }

    except urllib.error.HTTPError as e:
        err_msg = str(e)
        try:
            err_data = json.loads(e.read().decode("utf-8"))
            err_msg = err_data.get("error", {}).get("message", str(e))
        except Exception:
            pass

        return {
            "success": False,
            "error": f"HTTP {e.code}: {err_msg}",
            "status_code": e.code,
            "raw": None
        }

    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"Network Error: {e.reason}",
            "status_code": 0,
            "raw": None
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected Error: {str(e)}",
            "status_code": 0,
            "raw": None
        }


def main():
    print("=" * 65)
    print("✨ Google Gemini API Call Test - hello_gemini.py")
    print("=" * 65)

    # 1. Read API Key and Model from environment (.env)
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or ""
    model = os.environ.get("GEMINI_MODEL") or "gemini-1.5-flash"

    # Mask key for secure logging
    masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else ("(Not Set)" if not api_key else "****")

    print(f"🔑 API Key Configured : {masked_key}")
    print(f"🤖 Configured Model   : {model}")

    if not api_key:
        print("\n⚠️  No Google API Key detected!")
        print("Please add your key into the .env file in the project root:")
        print("    GOOGLE_API_KEY=your_gemini_api_key_here")
        print("\nGet a free Gemini API key at: https://aistudio.google.com/")
        print("=" * 65)
        sys.exit(1)

    # 2. Determine prompt
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:]).strip()
    else:
        prompt = "Hello Gemini! Please introduce yourself in 1 sentence and share 2 essential daily wellness habits."

    print(f"\n📤 Sending Prompt to Gemini [{model}]:")
    print(f'   "{prompt}"')
    print("\n⏳ Contacting Gemini API, please wait...")

    start_time = time.time()
    result = call_gemini(prompt=prompt, api_key=api_key, model=model)
    elapsed = time.time() - start_time

    # If the user specified a custom/unsupported model name that caused a 404, offer fallback
    if not result["success"] and result.get("status_code") == 404 and model != "gemini-1.5-flash":
        print(f"\n⚠️ Model '{model}' not found on Gemini API (HTTP 404). Retrying with 'gemini-1.5-flash'...")
        model = "gemini-1.5-flash"
        result = call_gemini(prompt=prompt, api_key=api_key, model=model)

    print("-" * 65)
    if result["success"]:
        print(f"✅ Success! Response received in {elapsed:.2f}s (Status {result['status_code']}):\n")
        print(result["text"])
        print("-" * 65)
    else:
        print(f"❌ Gemini API Call Failed (Elapsed: {elapsed:.2f}s):\n")
        print(f"   {result['error']}")
        print("-" * 65)
        print("💡 Troubleshooting Tips:")
        print("1. Verify your API key at https://aistudio.google.com/")
        print("2. Confirm that the Generative Language API is enabled on your Google Cloud project.")
        print("3. Check that your GEMINI_MODEL in .env is set to a valid model (e.g. gemini-1.5-flash).")

    print("=" * 65)


if __name__ == "__main__":
    main()
