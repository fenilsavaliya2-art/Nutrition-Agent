"""
Nutrition Agentic AI — Flask Backend
Provides REST API endpoints for the web application.
"""

import os
import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from agent import get_agent
from guardrails import sanitize_user_input, check_harmful_content

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "nutrition_ai_dev_secret")
CORS(app)

# Ensure plans directory exists
PLANS_DIR = os.path.join(os.path.dirname(__file__), "saved_plans")
os.makedirs(PLANS_DIR, exist_ok=True)


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main web application."""
    return send_from_directory("templates", "index.html")


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Nutrition Agentic AI",
        "model": "IBM Granite LLM",
        "timestamp": datetime.datetime.now().isoformat()
    })


@app.route("/api/generate-plan", methods=["POST"])
def generate_plan():
    """
    Main endpoint: generate personalized nutrition plan.
    Expects JSON body with user profile.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided."}), 400

        # Sanitize inputs
        profile = {
            "name": sanitize_user_input(data.get("name", "")),
            "age": str(data.get("age", "")),
            "diet_preference": sanitize_user_input(data.get("diet_preference", "")),
            "medical_history": sanitize_user_input(data.get("medical_history", "None")),
            "city": sanitize_user_input(data.get("city", "")),
            "country": sanitize_user_input(data.get("country", "")),
        }

        # Run agent pipeline
        agent = get_agent()
        result = agent.run(profile)

        if result["status"] == "success":
            # Auto-save the plan
            filename = _save_plan_to_file(profile, result["plan_markdown"])
            result["saved_file"] = filename

        return jsonify(result)

    except Exception as e:
        print(f"[API Error] /api/generate-plan: {e}")
        return jsonify({"status": "error", "message": "Internal server error. Please try again."}), 500


@app.route("/api/query", methods=["POST"])
def answer_query():
    """
    Query Resolution Agent endpoint.
    Answers user nutrition questions.
    """
    try:
        data = request.get_json()
        if not data or not data.get("query"):
            return jsonify({"status": "error", "message": "Query is required."}), 400

        query = sanitize_user_input(data.get("query", ""))
        profile = data.get("profile", {})

        # Guardrail check
        is_safe, reason = check_harmful_content(query)
        if not is_safe:
            return jsonify({
                "status": "blocked",
                "message": reason,
                "answer": f"⚠️ {reason}"
            })

        agent = get_agent()
        answer = agent.answer_query(query, profile)

        return jsonify({
            "status": "success",
            "answer": answer,
            "query": query
        })

    except Exception as e:
        print(f"[API Error] /api/query: {e}")
        return jsonify({"status": "error", "message": "Could not process query."}), 500


@app.route("/api/save-plan", methods=["POST"])
def save_plan():
    """Save a nutrition plan to a .md file."""
    try:
        data = request.get_json()
        plan_markdown = data.get("plan_markdown", "")
        profile = data.get("profile", {})

        if not plan_markdown:
            return jsonify({"status": "error", "message": "No plan content provided."}), 400

        filename = _save_plan_to_file(profile, plan_markdown)
        return jsonify({
            "status": "success",
            "message": f"Plan saved to {filename}",
            "filename": filename
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/plans", methods=["GET"])
def list_plans():
    """List all saved nutrition plans."""
    try:
        files = [f for f in os.listdir(PLANS_DIR) if f.endswith(".md")]
        files.sort(reverse=True)
        return jsonify({"status": "success", "plans": files})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/plans/<filename>", methods=["GET"])
def get_plan(filename):
    """Retrieve a saved nutrition plan."""
    try:
        # Security: only allow .md files, no path traversal
        if not filename.endswith(".md") or "/" in filename or "\\" in filename:
            return jsonify({"status": "error", "message": "Invalid filename."}), 400

        filepath = os.path.join(PLANS_DIR, filename)
        if not os.path.exists(filepath):
            return jsonify({"status": "error", "message": "Plan not found."}), 404

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        return jsonify({"status": "success", "content": content, "filename": filename})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────

def _save_plan_to_file(profile: dict, plan_markdown: str) -> str:
    """Save plan to a .md file with timestamp."""
    name = profile.get("name", "user").replace(" ", "_").lower()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"nutrition_plan_{name}_{timestamp}.md"
    filepath = os.path.join(PLANS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(plan_markdown)

    print(f"[Plan Saved] {filepath}")
    return filename


# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  Nutrition Agentic AI -- IBM Granite LLM")
    print("  Starting Flask server...")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 60)
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=os.getenv("FLASK_DEBUG", "False").lower() == "true"
    )
