# 🌿 Vitalis: Health Awareness Assistant

A web-based, evidence-informed **Health Awareness & Lifestyle Education Chatbot** engineered with strict medical safety guardrails, an interactive health literacy quiz engine, and a transparent system prompt explanation module.

---

## 📌 Project Overview

**Vitalis Health Assistant** is built to promote public health awareness, preventive lifestyle habits, and health literacy. It provides accessible, science-backed guidance on hydration, restorative sleep, nutrition, cardiovascular health, sun safety, and stress resilience.

> **Crucial Educational Boundary:**
> Vitalis is **strictly an educational and informational tool**. It does **not** provide medical diagnosis, prescribe drugs, analyze individual pathology, or handle acute medical emergencies. It is designed to empower individuals with general literacy while directing clinical concerns to licensed healthcare providers.

---

## ✨ Key Features

- 💬 **Evidence-Informed Educational Chat:**
  - Conversational advice on hydration baselines, sleep hygiene, WHO physical activity recommendations, dietary fiber, and stress management.
  - Interactive suggested topic chips and quick questions.
- 🔑 **Google Gemini API Key Integration:**
  - Seamlessly powered by Google Gemini (e.g. `gemini-1.5-flash`) for dynamic, evidence-based responses.
  - Flexible configuration: set via `.env` file (`GOOGLE_API_KEY=...`) or directly via the **"Google API"** button in the web UI.
  - Zero-dependency REST API implementation using Python standard library.
  - Automatic graceful fallback to the curated offline knowledge base if no API key is provided.
- 📜 **Search & Conversation History Memory:**
  - **Sidebar History Drawer:** Automatically tracks and displays previous searches and queries with relative timestamps.
  - **Multi-Turn Chat Context:** Assistant maintains memory of what the user searched or asked previously in the session.
  - Ask *"What did I search before?"* or *"Can you expand on what I asked earlier?"* and the assistant references prior searches directly.
  - Persistent browser storage (`localStorage`) so search history remains across page reloads.
- 🛡️ **Strict Safety & Ethical Guardrails:**
  - **Emergency Detection:** Regex-based interception of life-threatening cues (chest pain, stroke signs, difficulty breathing, severe bleeding, anaphylaxis, crisis) with immediate 911 / emergency hotline escalation.
  - **No-Diagnosis Policy:** Politely intercepts diagnostic requests ("Do I have bronchitis?", "Diagnose my rash") and explains why clinical consultation is required.
  - **Zero Prescription Claims:** Prohibits medication dosing or treatment plans.
  - **Mandatory Disclaimers:** Visible educational disclaimers embedded across all responses and interface views.
- ℹ️ **Sidebar: Prompt Explanation Button:**
  - Opens a dedicated architectural dashboard revealing the underlying system prompt design, persona constraints, safety rules, and interactive guardrail testing triggers.
- 🧠 **Sidebar: Health Awareness Quiz Button:**
  - Multi-topic health literacy quiz (8 curated questions covering exercise, hydration, sleep, antibiotics, nutrition, UV protection, and stress).
  - Real-time answer checking with instant visual cues and evidence-based explanations citing WHO, CDC, and AHA standards.
  - End-of-quiz score summary, percentage calculation, and detailed question-by-question review.
- 🎨 **Modern Aesthetics:**
  - Deep slate/emerald health-tech palette, subtle glassmorphism, responsive collapsible sidebar, smooth animations, and clean typography (Outfit & Plus Jakarta Sans).

---

## 🗂️ Project Structure

```text
├── app.py                      # Main Flask application with REST API endpoints
├── health_assistant/           # Backend core logic package
│   ├── __init__.py             # Package initializer exposing chatbot, quiz, & load_env
│   ├── chatbot.py              # Safety guardrails, intent parser, knowledge base & CLI
│   ├── env_loader.py           # Resilient .env configuration file loader
│   ├── gemini_service.py       # Google Gemini API client with safety prompts
│   └── quiz_data.py            # Question bank with explanations & categories
├── static/                     # Frontend static assets
│   ├── css/
│   │   └── style.css           # Glassmorphic stylesheet & responsive rules
│   └── js/
│       └── app.js              # Single-page client logic & quiz engine
├── templates/                  # Frontend HTML templates
│   └── index.html              # Modern semantic UI with Sidebar, Chat, Prompt & Quiz
├── .env                        # Local environment configuration file (API keys, port)
├── .env.example                # Example environment configuration template
├── requirements.txt            # Python dependencies (Flask, Werkzeug, python-dotenv)
├── .gitignore                  # Git ignore rules for Python, IDEs, and OS files
├── test_chatbot.py             # Automated unit tests for safety filters & routes
└── README.md                   # Complete documentation & GitHub setup guide
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.6 or higher
- `pip` (Python package manager)
- Git (for version control and uploading to GitHub)

### 1. Clone or Download the Repository

```bash
git clone https://github.com/<YOUR_USERNAME>/health-awareness-assistant.git
cd health-awareness-assistant
```

### 2. Create and Activate a Virtual Environment (Recommended)

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The application will start locally at:
👉 **`http://localhost:5000`** (or `http://127.0.0.1:5000`)

Open your web browser and navigate to this URL to interact with the assistant.

---

## 🧪 Automated Testing

Run the test suite to verify the guardrails, emergency detection, and API endpoints:

```bash
python -m unittest test_chatbot.py -v
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the main single-page application |
| `GET` | `/api/health` | Health check endpoint |
| `POST` | `/api/chat` | Processes user chat input with multi-turn history & optional Google API key |
| `GET` | `/api/api-key/status` | Checks if a Google Gemini API key is configured and active |
| `POST` | `/api/api-key/validate` | Tests and validates a user-provided Google API key |
| `GET` | `/api/prompt-explanation` | Returns system prompt details, role, and guardrail rules |
| `GET` | `/api/quiz` | Returns health awareness questions without answers |
| `POST` | `/api/quiz/evaluate` | Grades user quiz answers and returns scores with explanations |

---

## 🐙 Step-by-Step GitHub Upload Instructions

Follow these steps to upload this project directly to your GitHub account:

### Step 1: Create a New Repository on GitHub
1. Log in to [GitHub](https://github.com/).
2. Click the **`+`** icon in the top right corner and select **New repository**.
3. Enter a repository name (e.g., `health-awareness-assistant`).
4. Set visibility to **Public** (or **Private**).
5. **Do NOT** initialize with a README, .gitignore, or license (these are already included in this project).
6. Click **Create repository**.

### Step 2: Initialize Git and Commit Locally
Open your terminal or PowerShell in the root folder of this project (`health-awareness-assistant`):

```bash
# 1. Initialize local git repository
git init

# 2. Add all project files
git add .

# 3. Create initial commit
git commit -m "Initial commit: Health Awareness Assistant with Prompt Explanation & Quiz"
```

### Step 3: Link to GitHub and Push

```bash
# 4. Rename main branch (if needed)
git branch -M main

# 5. Add your GitHub repository as the remote origin
# (Replace <YOUR_USERNAME> and <REPO_NAME> with your actual details)
git remote add origin https://github.com/<YOUR_USERNAME>/health-awareness-assistant.git

# 6. Push code to GitHub
git push -u origin main
```

---

## ⚖️ Educational & Medical Disclaimer

**Vitalis Health Awareness Assistant** is developed exclusively for educational, informational, and wellness literacy purposes. 

- It does **not** give clinical diagnoses.
- It does **not** prescribe or alter drug treatments.
- It is **not** an emergency medical dispatch service.
- If you believe you may have a medical emergency, call your local emergency services (such as **911** in the US/Canada, **999** in the UK, or **112** in Europe) immediately.
- Always seek the guidance of a physician or other qualified health professional with any questions regarding personal medical conditions or symptoms.
