<div align="center">

# 🥗 Nutrition Agentic AI
### Powered by IBM Granite LLM via IBM watsonx.ai

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![IBM watsonx](https://img.shields.io/badge/IBM-watsonx.ai-054ADA?style=for-the-badge&logo=ibm&logoColor=white)](https://www.ibm.com/watsonx)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**A web-based Agentic AI application that generates personalized, medically-aware nutrition plans using IBM Granite LLM — with built-in AI ethics, safety guardrails, and a real-time chat assistant.**

[🚀 Quick Start](#-quick-start) • [📐 Architecture](#-architecture) • [🔑 IBM Granite Setup](#-ibm-granite-llm-setup) • [📡 API Reference](#-api-reference) • [🛡️ AI Ethics](#️-ai-ethics--guardrails)

</div>

---

## 📸 Application Preview

```
┌─────────────────────────────────────────────────────────────┐
│  🥗 Nutrition Agentic AI          [IBM Granite Badge]        │
├──────────────────────────┬──────────────────────────────────┤
│  👤 User Profile Form    │  📋 Plan  💬 Chat  📁 Saved      │
│                          │                                   │
│  Name: Priya Sharma      │  📊 1900 kcal | 119g P | 63g F   │
│  Age: 32                 │                                   │
│  Diet: Vegetarian ▼      │  # 🥗 Personalized Plan           │
│  ☑ Diabetes              │  ## 7-Day Meal Plan               │
│  ☑ Blood Pressure        │  Mon | Breakfast | Oats + Dal..  │
│  City: Mumbai            │  Tue | Lunch    | Chickpea...    │
│  Country: India          │                                   │
│                          │  ⚕️ Medical Disclaimer            │
│  [✨ Generate My Plan]   │                                   │
└──────────────────────────┴──────────────────────────────────┘
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 👤 **Profile Collection** | Name, age, diet preference (Veg / Non-Veg / Vegan), medical history (multi-select checkboxes), city, country |
| 🏥 **Medical Awareness** | Adapts plan for Diabetes, Blood Pressure, Heart Disease, Thyroid, Kidney Issues |
| 🤖 **IBM Granite LLM** | Connects to IBM watsonx.ai Granite-13b-Instruct; demo mode if no API key |
| 📅 **7-Day Meal Plan** | Breakfast, mid-morning snack, lunch, evening snack, dinner, hydration for every day |
| 📊 **Nutritional Targets** | Daily calories, protein, carbs, fats, fibre, water — calculated per age group |
| 💬 **Chat Agent** | Ask NutriGuide AI any nutrition question; quick-question shortcuts included |
| 💾 **Save to .md** | Every plan auto-saved as `nutrition_plan_<name>_<timestamp>.md`; downloadable from UI |
| 🛡️ **Guardrails** | Blocks 15+ harmful topics; sanitises inputs; prevents prompt injection |
| ⚕️ **Medical Disclaimer** | Mandatory disclaimer on every generated plan |
| 📱 **Responsive Dark UI** | Works on desktop and mobile browsers |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 Web Browser  (Frontend)                         │
│         HTML5 + CSS3 + Vanilla JavaScript                       │
│   Profile Form │ Plan Viewer │ Chat │ Saved Plans               │
└─────────────────────────┬───────────────────────────────────────┘
                          │  REST API  (JSON over HTTP)
┌─────────────────────────▼───────────────────────────────────────┐
│              Flask Backend  ·  app.py                           │
│  POST /api/generate-plan  │  POST /api/query                    │
│  GET  /api/plans          │  GET  /api/plans/<filename>         │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│           Nutrition Agent Pipeline  ·  agent.py                 │
│                                                                 │
│  [Agent 1]  Profile Validator                                   │
│       ↓                                                         │
│  [Agent 2]  Medical Context Analyzer  ←  MEDICAL_ADAPTATIONS   │
│       ↓                                                         │
│  [Agent 3]  Caloric Needs Calculator  ←  Mifflin-St Jeor       │
│       ↓                                                         │
│  [Agent 4]  Meal Plan Builder         ←  NUTRITION_DATABASE     │
│       ↓                                                         │
│  [Agent 5]  IBM Granite LLM           ←  watsonx.ai API        │
│       ↓                                                         │
│  [Agent 6]  Guardrail Reviewer + Formatter                      │
│       ↓                                                         │
│  [Output]   Markdown Plan  →  saved_plans/*.md                  │
└─────────────────────────────────────────────────────────────────┘
          ↑
┌─────────┴───────────────────────────────────────────────────────┐
│           guardrails.py  —  Ethics & Safety Layer               │
│  Blocked topics · HAM principles · Medical disclaimer           │
└─────────────────────────────────────────────────────────────────┘
```

### Agentic AI SDLC — 6 Phases

| Phase | Agent | Responsibility |
|-------|-------|----------------|
| **1 — Requirements** | Profile Validator | Collect & validate user profile; sanitise inputs |
| **2 — Analysis** | Medical Context Agent | Detect conditions (diabetes, BP…); map dietary adaptations |
| **2b — Analysis** | Caloric Needs Agent | Calculate daily kcal, macros via age-based estimation |
| **3 — Planning** | Meal Plan Builder | Generate 7-day plan from diet-specific nutrition database |
| **4 — Generation** | IBM Granite LLM Agent | Send structured prompt; get personalised narrative |
| **5 — Review** | Guardrail Agent | Scan output for harmful content; enforce ethics |
| **6 — Delivery** | Formatter & Save Agent | Format markdown; auto-save `.md`; serve to UI |

---

## 📁 Project Structure

```
NutritionAgent-IBMBob/
│
├── run_nutrition_ai.bat          ← Windows one-click launcher
├── install_dependencies.bat      ← Install packages only
├── README.md                     ← This file
│
└── nutrition_ai/
    ├── app.py                    ← Flask web server & REST API
    ├── agent.py                  ← IBM Granite agentic pipeline (6 agents)
    ├── guardrails.py             ← AI ethics, safety & medical disclaimer
    ├── requirements.txt          ← Python dependencies
    ├── .env.example              ← Credentials template (copy → .env)
    │
    ├── templates/
    │   └── index.html            ← Full dark-theme single-page web app
    │
    └── saved_plans/
        └── *.md                  ← Auto-generated nutrition plan files
```

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.9 or higher | [Download](https://www.python.org/downloads/) — tick "Add to PATH" |
| pip | bundled with Python | Updated automatically |
| Git | any recent | [Download](https://git-scm.com/downloads) |
| IBM watsonx.ai | — | Optional — see [IBM Granite Setup](#-ibm-granite-llm-setup) |

---

### Option 1 — Windows One-Click (Recommended)

```bat
double-click  run_nutrition_ai.bat
```

The script automatically:
1. Checks Python installation
2. Creates a virtual environment (`nutrition_ai/venv/`)
3. Installs all dependencies from `requirements.txt`
4. Copies `.env.example` → `.env` (first run)
5. Starts Flask at **http://localhost:5000**
6. Opens your default browser

---

### Option 2 — Manual (Windows / macOS / Linux)

```bash
# 1. Clone the repository
git clone https://github.com/YogeshRaje/NutritionAgent-IBMBob.git
cd NutritionAgent-IBMBob

# 2. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r nutrition_ai/requirements.txt

# 4. Configure credentials
cp nutrition_ai/.env.example nutrition_ai/.env
# Edit nutrition_ai/.env with your IBM watsonx.ai credentials

# 5. Start the application
cd nutrition_ai
python app.py
```

Open **http://localhost:5000** in your browser.

---

## 🔑 IBM Granite LLM Setup

### Step 1 — Create IBM Cloud Account
Go to [https://cloud.ibm.com](https://cloud.ibm.com) and sign up for a free account.

### Step 2 — Provision watsonx.ai
- Navigate to **Catalog → AI / Machine Learning → Watson Machine Learning**
- Create a service instance (Lite tier is free)
- Launch **watsonx.ai Studio** and create a new project

### Step 3 — Get Credentials
- **API Key**: IBM Cloud → Manage → Access (IAM) → API Keys → Create
- **Project ID**: watsonx.ai Studio → Your Project → Manage → General → Project ID

### Step 4 — Configure `.env`

```env
# nutrition_ai/.env

WATSONX_API_KEY=your_actual_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com

FLASK_SECRET_KEY=change_me_in_production
FLASK_DEBUG=False
```

> **Without an API key** the app runs in **Demo Mode** — all agentic pipeline steps (medical analysis, 7-day meal planning, guardrails, `.md` save) work fully. Only the IBM Granite narrative section shows a demo placeholder.

### Model Used

```
ibm/granite-13b-instruct-v2
```
Parameters: `max_new_tokens=1500`, `temperature=0.7`, `top_p=0.9`, `repetition_penalty=1.1`

---

## 📡 API Reference

### `POST /api/generate-plan`
Generate a personalised nutrition plan.

**Request Body**
```json
{
  "name": "Priya Sharma",
  "age": "32",
  "diet_preference": "Vegetarian",
  "medical_history": "Diabetes, Blood Pressure",
  "city": "Mumbai",
  "country": "India"
}
```

**Success Response**
```json
{
  "status": "success",
  "message": "Nutrition plan generated successfully.",
  "plan_markdown": "# 🥗 Personalized Nutrition Plan\n...",
  "caloric_needs": {
    "daily_calories": 1900,
    "protein_g": 119,
    "carbs_g": 214,
    "fat_g": 63,
    "fiber_g": 25,
    "water_liters": 2.5
  },
  "conditions_detected": ["diabetes", "blood pressure"],
  "saved_file": "nutrition_plan_priya_sharma_20240615_143022.md"
}
```

---

### `POST /api/query`
Ask NutriGuide AI a nutrition question.

**Request Body**
```json
{
  "query": "What foods help lower blood sugar naturally?",
  "profile": {
    "name": "Priya",
    "age": "32",
    "diet_preference": "Vegetarian",
    "medical_history": "Diabetes"
  }
}
```

**Success Response**
```json
{
  "status": "success",
  "answer": "Foods that help lower blood sugar...",
  "query": "What foods help lower blood sugar naturally?"
}
```

---

### `GET /api/plans`
List all saved `.md` nutrition plans.

```json
{
  "status": "success",
  "plans": [
    "nutrition_plan_priya_sharma_20240615_143022.md",
    "nutrition_plan_demo_user_sample.md"
  ]
}
```

---

### `GET /api/plans/<filename>`
Retrieve the content of a saved plan.

### `GET /api/health`
Health-check endpoint — returns service status and timestamp.

---

## 🛡️ AI Ethics & Guardrails

### HAM Principles
| Principle | Description |
|-----------|-------------|
| 🤝 **Helpful** | Evidence-based, practical nutrition guidance tailored to each user |
| 🎯 **Accurate** | Relies only on established nutritional science — never invents facts |
| ⚕️ **Medical-safe** | Never prescribes medications or treatments; always defers to healthcare professionals |

### Blocked Topics (15+)
`drug` · `narcotic` · `steroid` · `anabolic` · `laxative abuse` · `starvation diet` · `eating disorder` · `purging` · `self-harm` · `suicide` · `medication overdose` · `extreme fasting` · `harmful supplement` · `unregulated supplement`

### Input Sanitisation
- Strips prompt-injection markers (`###`, `SYSTEM:`, `IGNORE PREVIOUS`, `<|`)
- Caps input length at 2 000 characters
- Validates all required fields before entering the pipeline

### Medical Disclaimer
Every generated plan includes a mandatory disclaimer stating it is **informational only** and not a substitute for professional medical advice.

---

## 🧪 Running Tests

```bash
# Health check
curl http://localhost:5000/api/health

# Generate plan (PowerShell)
Invoke-RestMethod -Uri http://localhost:5000/api/generate-plan `
  -Method POST -ContentType "application/json" `
  -Body '{"name":"Test User","age":"30","diet_preference":"Vegetarian","medical_history":"None","city":"Delhi","country":"India"}'

# Generate plan (bash / curl)
curl -X POST http://localhost:5000/api/generate-plan \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","age":"30","diet_preference":"Vegetarian","medical_history":"None","city":"Delhi","country":"India"}'
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "Add: your feature description"`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## ⚕️ Medical Disclaimer

> This application is for **informational and educational purposes only**. It does **NOT** constitute professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider, registered dietitian, or licensed nutritionist before making significant dietary changes, especially if you have diabetes, blood pressure, heart disease, kidney disease, or any other chronic condition.

---

<div align="center">

**Built with ❤️ using IBM Granite LLM · IBM watsonx.ai · Flask · Python**

[🐛 Report Bug](https://github.com/YogeshRaje/NutritionAgent-IBMBob/issues) · [💡 Request Feature](https://github.com/YogeshRaje/NutritionAgent-IBMBob/issues)

</div>
