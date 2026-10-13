"""
Nutrition Agentic AI — IBM Granite LLM Agent
Implements multi-step agentic reasoning:
  1. Profile Collection Agent
  2. Medical Context Agent
  3. Nutrition Planning Agent
  4. Query Resolution Agent
  5. Plan Formatting Agent
"""

import os
import datetime
from dotenv import load_dotenv
from guardrails import (
    SYSTEM_PROMPT, MEDICAL_DISCLAIMER,
    check_harmful_content, sanitize_user_input, validate_user_profile
)

load_dotenv()

# ──────────────────────────────────────────────
# IBM Granite LLM Client
# ──────────────────────────────────────────────
try:
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    IBM_SDK_AVAILABLE = True
except ImportError:
    IBM_SDK_AVAILABLE = False


class GraniteLLMClient:
    """IBM Granite LLM interface with fallback demo mode."""

    MODEL_ID = "ibm/granite-13b-instruct-v2"

    def __init__(self):
        self.api_key = os.getenv("WATSONX_API_KEY", "")
        self.project_id = os.getenv("WATSONX_PROJECT_ID", "")
        self.url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        self.model = None
        self.demo_mode = True

        if IBM_SDK_AVAILABLE and self.api_key and self.api_key != "your_ibm_watsonx_api_key_here":
            try:
                credentials = Credentials(url=self.url, api_key=self.api_key)
                self.model = ModelInference(
                    model_id=self.MODEL_ID,
                    credentials=credentials,
                    project_id=self.project_id,
                    params={
                        GenParams.MAX_NEW_TOKENS: 1500,
                        GenParams.TEMPERATURE: 0.7,
                        GenParams.TOP_P: 0.9,
                        GenParams.REPETITION_PENALTY: 1.1,
                    }
                )
                self.demo_mode = False
                print("[GraniteLLM] OK  Connected to IBM watsonx.ai - Granite model loaded.")
            except Exception as e:
                print(f"[GraniteLLM] WARN IBM watsonx connection failed: {e}")
                print("[GraniteLLM] --> Falling back to demo mode.")
                self.demo_mode = True
        else:
            print("[GraniteLLM] INFO Running in DEMO mode (no valid API key found).")

    def generate(self, prompt: str) -> str:
        """Send prompt to Granite LLM and return response."""
        if self.demo_mode:
            return self._demo_response(prompt)
        try:
            full_prompt = f"{SYSTEM_PROMPT}\n\nUser Request:\n{prompt}"
            response = self.model.generate_text(prompt=full_prompt)
            return response
        except Exception as e:
            print(f"[GraniteLLM] Error: {e}")
            return self._demo_response(prompt)

    def _demo_response(self, prompt: str) -> str:
        """
        Structured demo response that simulates IBM Granite output.
        Used when API credentials are not configured.
        """
        return f"[DEMO MODE — Configure IBM watsonx.ai API key for real Granite responses]\n\n{prompt}"


# ──────────────────────────────────────────────
# Agentic Tools (Function Calling)
# ──────────────────────────────────────────────

NUTRITION_DATABASE = {
    "vegetarian": {
        "proteins": ["lentils", "chickpeas", "tofu", "paneer", "Greek yogurt", "quinoa", "edamame", "black beans"],
        "carbs": ["brown rice", "whole wheat bread", "oats", "sweet potato", "millet", "barley"],
        "fats": ["avocado", "almonds", "walnuts", "flaxseeds", "olive oil", "chia seeds"],
        "vegetables": ["spinach", "broccoli", "carrots", "bell peppers", "kale", "tomatoes", "cucumber"]
    },
    "non-vegetarian": {
        "proteins": ["chicken breast", "salmon", "tuna", "eggs", "turkey", "lean beef", "sardines"],
        "carbs": ["brown rice", "whole wheat bread", "oats", "sweet potato", "quinoa"],
        "fats": ["salmon (omega-3)", "avocado", "almonds", "olive oil", "walnuts"],
        "vegetables": ["broccoli", "spinach", "asparagus", "zucchini", "bell peppers", "kale"]
    },
    "vegan": {
        "proteins": ["lentils", "chickpeas", "tofu", "tempeh", "seitan", "hemp seeds", "spirulina"],
        "carbs": ["brown rice", "oats", "quinoa", "sweet potato", "whole grain pasta"],
        "fats": ["avocado", "flaxseeds", "chia seeds", "walnuts", "coconut", "sunflower seeds"],
        "vegetables": ["kale", "spinach", "broccoli", "Brussels sprouts", "carrots", "beets"]
    }
}

MEDICAL_ADAPTATIONS = {
    "diabetes": {
        "avoid": ["white rice", "white bread", "sugary drinks", "candy", "pastries", "fruit juice", "white potato"],
        "prefer": ["low-GI foods", "fiber-rich vegetables", "lean proteins", "nuts", "whole grains"],
        "tips": [
            "Space meals every 3–4 hours to maintain blood sugar levels",
            "Include fiber at every meal to slow glucose absorption",
            "Limit carbohydrates to 45–60g per meal",
            "Choose complex carbs over simple carbs",
            "Monitor blood glucose before and after meals"
        ]
    },
    "blood pressure": {
        "avoid": ["excess salt (>1500mg/day)", "processed meats", "canned soups", "pickles", "alcohol", "caffeine"],
        "prefer": ["potassium-rich foods", "DASH diet foods", "low-sodium options", "magnesium-rich foods"],
        "tips": [
            "Follow the DASH (Dietary Approaches to Stop Hypertension) diet",
            "Reduce sodium intake to less than 1500mg per day",
            "Increase potassium with bananas, sweet potatoes, and leafy greens",
            "Limit alcohol to 1 drink/day (women) or 2 drinks/day (men)",
            "Include omega-3 fatty acids to support heart health"
        ]
    },
    "none": {
        "avoid": [],
        "prefer": ["balanced macronutrients", "variety of whole foods"],
        "tips": [
            "Maintain a balanced diet with all food groups",
            "Stay hydrated with 8–10 glasses of water daily",
            "Limit processed and ultra-processed foods",
            "Include colorful vegetables and fruits daily"
        ]
    }
}


def tool_analyze_medical_needs(medical_history: str) -> dict:
    """Agent Tool: Analyze medical history and return dietary adaptations."""
    history_lower = medical_history.lower()
    adaptations = {}

    if "diabetes" in history_lower or "diabetic" in history_lower or "blood sugar" in history_lower:
        adaptations["diabetes"] = MEDICAL_ADAPTATIONS["diabetes"]

    if "blood pressure" in history_lower or "hypertension" in history_lower or "bp" in history_lower:
        adaptations["blood pressure"] = MEDICAL_ADAPTATIONS["blood pressure"]

    if not adaptations:
        adaptations["general"] = MEDICAL_ADAPTATIONS["none"]

    return adaptations


def tool_get_caloric_needs(age: int, diet_preference: str) -> dict:
    """Agent Tool: Calculate approximate daily caloric needs."""
    # Simplified Mifflin-St Jeor estimate (moderate activity, gender-neutral baseline)
    if age < 18:
        base = 2200
    elif age < 30:
        base = 2000
    elif age < 50:
        base = 1900
    elif age < 65:
        base = 1800
    else:
        base = 1700

    return {
        "daily_calories": base,
        "protein_g": round(base * 0.25 / 4),    # 25% protein
        "carbs_g": round(base * 0.45 / 4),        # 45% carbs
        "fat_g": round(base * 0.30 / 9),           # 30% fat
        "fiber_g": 25,
        "water_liters": 2.5
    }


def tool_build_meal_plan(profile: dict, medical_adaptations: dict, caloric_needs: dict) -> dict:
    """Agent Tool: Build a structured 7-day meal plan."""
    diet = profile.get("diet_preference", "vegetarian").lower()
    foods = NUTRITION_DATABASE.get(diet, NUTRITION_DATABASE["vegetarian"])

    # Identify conditions
    has_diabetes = "diabetes" in medical_adaptations
    has_bp = "blood pressure" in medical_adaptations

    # Sample meal templates
    meal_plan = {
        "Monday": _day_plan(foods, "Monday", has_diabetes, has_bp),
        "Tuesday": _day_plan(foods, "Tuesday", has_diabetes, has_bp),
        "Wednesday": _day_plan(foods, "Wednesday", has_diabetes, has_bp),
        "Thursday": _day_plan(foods, "Thursday", has_diabetes, has_bp),
        "Friday": _day_plan(foods, "Friday", has_diabetes, has_bp),
        "Saturday": _day_plan(foods, "Saturday", has_diabetes, has_bp),
        "Sunday": _day_plan(foods, "Sunday", has_diabetes, has_bp),
    }
    return meal_plan


def _day_plan(foods: dict, day: str, has_diabetes: bool, has_bp: bool) -> dict:
    """Generate a single day meal plan."""
    proteins = foods["proteins"]
    carbs = foods["carbs"]
    fats = foods["fats"]
    vegs = foods["vegetables"]

    # Rotate based on day index
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    idx = days.index(day) if day in days else 0

    p = proteins[idx % len(proteins)]
    c = carbs[idx % len(carbs)]
    f = fats[idx % len(fats)]
    v1 = vegs[idx % len(vegs)]
    v2 = vegs[(idx + 2) % len(vegs)]

    # Carb note for diabetes
    carb_note = " (small portion, ½ cup)" if has_diabetes else " (1 cup)"
    salt_note = " (no added salt)" if has_bp else ""

    return {
        "breakfast": f"1 bowl {c}{carb_note} + {p} (100g) + {v1}{salt_note} + green tea",
        "mid_morning": f"Handful of {f} + 1 fruit (apple/pear)" + (" — avoid banana if diabetic" if has_diabetes else ""),
        "lunch": f"{p} (150g) with {v1} & {v2} salad + {c}{carb_note}{salt_note} + glass of water",
        "evening_snack": f"Herbal tea + {f} (small handful) + cucumber slices",
        "dinner": f"Steamed {v2} + {p} (100g) + light soup{salt_note} + {c}{carb_note}",
        "hydration": "8–10 glasses of water; coconut water is acceptable"
    }


# ──────────────────────────────────────────────
# Main Nutrition Agent
# ──────────────────────────────────────────────

class NutritionAgent:
    """
    Multi-step Agentic AI for personalized nutrition planning.
    Follows Agentic SDLC phases:
      Phase 1 — Requirements (profile collection)
      Phase 2 — Analysis (medical + caloric assessment)
      Phase 3 — Planning (meal plan generation)
      Phase 4 — Generation (LLM-enhanced narrative)
      Phase 5 — Review (guardrail validation)
      Phase 6 — Delivery (formatted output + save)
    """

    def __init__(self):
        self.llm = GraniteLLMClient()

    def run(self, profile: dict) -> dict:
        """
        Execute the full agentic pipeline.
        Returns dict with keys: plan_markdown, status, message
        """
        # ── Phase 1: Validate profile ──
        valid, msg = validate_user_profile(profile)
        if not valid:
            return {"status": "error", "message": msg, "plan_markdown": ""}

        # ── Phase 2: Medical Analysis Agent ──
        medical_adaptations = tool_analyze_medical_needs(
            profile.get("medical_history", "none")
        )

        # ── Phase 2b: Caloric Needs Agent ──
        caloric_needs = tool_get_caloric_needs(
            int(profile.get("age", 30)),
            profile.get("diet_preference", "vegetarian")
        )

        # ── Phase 3: Meal Plan Agent ──
        meal_plan = tool_build_meal_plan(profile, medical_adaptations, caloric_needs)

        # ── Phase 4: LLM Enhancement Agent ──
        llm_prompt = self._build_llm_prompt(profile, medical_adaptations, caloric_needs)
        llm_narrative = self.llm.generate(llm_prompt)

        # ── Phase 5: Guardrail Review ──
        is_safe, reason = check_harmful_content(llm_narrative)
        if not is_safe:
            llm_narrative = f"⚠️ Content filtered: {reason}"

        # ── Phase 6: Format & Deliver ──
        plan_md = self._format_plan(
            profile, medical_adaptations, caloric_needs, meal_plan, llm_narrative
        )

        return {
            "status": "success",
            "message": "Nutrition plan generated successfully.",
            "plan_markdown": plan_md,
            "caloric_needs": caloric_needs,
            "conditions_detected": list(medical_adaptations.keys())
        }

    def answer_query(self, query: str, profile: dict = None) -> str:
        """
        Query Resolution Agent — answers user nutrition questions.
        """
        query = sanitize_user_input(query)

        # Guardrail check
        is_safe, reason = check_harmful_content(query)
        if not is_safe:
            return f"⚠️ {reason}"

        context = ""
        if profile:
            context = (
                f"User context: {profile.get('name', 'User')}, "
                f"Age {profile.get('age', 'unknown')}, "
                f"{profile.get('diet_preference', 'general')} diet, "
                f"Medical history: {profile.get('medical_history', 'none')}."
            )

        prompt = f"""{context}

User Question: {query}

Please provide a helpful, evidence-based answer. If the question involves medical treatment or diagnosis, 
remind the user to consult a healthcare professional. Keep response concise and practical."""

        response = self.llm.generate(prompt)

        # Add brief disclaimer for medical topics
        medical_keywords = ["diabetes", "blood pressure", "heart", "kidney", "disease", "medication", "treatment"]
        if any(kw in query.lower() for kw in medical_keywords):
            response += "\n\n*⚕️ Always consult your doctor or registered dietitian for personalized medical guidance.*"

        return response

    def _build_llm_prompt(self, profile: dict, medical_adaptations: dict, caloric_needs: dict) -> str:
        conditions = ", ".join(medical_adaptations.keys()) if medical_adaptations else "none"
        return f"""
Generate a personalized nutrition plan for:
- Name: {profile.get('name')}
- Age: {profile.get('age')} years
- Diet Preference: {profile.get('diet_preference')}
- Medical History: {profile.get('medical_history', 'None')}
- Location: {profile.get('city')}, {profile.get('country')}
- Detected Conditions: {conditions}
- Daily Calorie Target: {caloric_needs['daily_calories']} kcal
- Protein Target: {caloric_needs['protein_g']}g | Carbs: {caloric_needs['carbs_g']}g | Fat: {caloric_needs['fat_g']}g

Please provide:
1. A brief personalized nutrition overview paragraph (2-3 sentences) acknowledging their specific needs.
2. Key nutritional guidelines for their conditions.
3. 3–5 specific food recommendations for their location/culture.
4. Hydration and lifestyle tips.
5. Foods to avoid given their medical history.

Use encouraging, respectful language. Format in clean markdown.
"""

    def _format_plan(self, profile, medical_adaptations, caloric_needs, meal_plan, llm_narrative) -> str:
        name = profile.get("name", "User")
        age = profile.get("age")
        diet = profile.get("diet_preference")
        history = profile.get("medical_history", "None reported")
        city = profile.get("city")
        country = profile.get("country")
        timestamp = datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p")
        conditions = list(medical_adaptations.keys())

        # Build conditions section
        conditions_section = ""
        for cond, data in medical_adaptations.items():
            if cond == "general":
                tips = "\n".join(f"- {t}" for t in data["tips"])
                conditions_section += f"\n### ✅ General Health Guidelines\n{tips}\n"
            else:
                avoid = ", ".join(data["avoid"]) if data["avoid"] else "None"
                prefer = ", ".join(data["prefer"])
                tips = "\n".join(f"- {t}" for t in data["tips"])
                conditions_section += f"""
### 🏥 {cond.title()} — Dietary Guidelines
**Foods to Avoid:** {avoid}
**Preferred Foods:** {prefer}
**Key Tips:**
{tips}
"""

        # Build weekly meal plan section
        meal_plan_section = ""
        for day, meals in meal_plan.items():
            meal_plan_section += f"""
#### {day}
| Meal | What to Eat |
|------|-------------|
| 🌅 Breakfast | {meals['breakfast']} |
| 🍎 Mid-Morning | {meals['mid_morning']} |
| 🍽️ Lunch | {meals['lunch']} |
| 🫖 Evening Snack | {meals['evening_snack']} |
| 🌙 Dinner | {meals['dinner']} |
| 💧 Hydration | {meals['hydration']} |
"""

        plan = f"""# 🥗 Personalized Nutrition Plan
## For: {name}

**Generated:** {timestamp}
**Location:** {city}, {country}
**Age:** {age} | **Diet:** {diet} | **Medical History:** {history}

---

## 📊 Daily Nutritional Targets

| Nutrient | Daily Target |
|----------|-------------|
| 🔥 Calories | {caloric_needs['daily_calories']} kcal |
| 💪 Protein | {caloric_needs['protein_g']} g |
| 🌾 Carbohydrates | {caloric_needs['carbs_g']} g |
| 🥑 Healthy Fats | {caloric_needs['fat_g']} g |
| 🌿 Fiber | {caloric_needs['fiber_g']} g |
| 💧 Water | {caloric_needs['water_liters']} liters |

---

## 🤖 AI Nutrition Assessment
*Powered by IBM Granite LLM*

{llm_narrative}

---

## 🏥 Medical & Dietary Conditions
{conditions_section}

---

## 📅 7-Day Meal Plan
{meal_plan_section}

---

## 💡 General Wellness Tips
- **Eat mindfully**: Chew slowly and eat without distractions.
- **Meal prep**: Prepare meals in advance to avoid unhealthy choices.
- **Sleep**: Aim for 7–9 hours; poor sleep increases hunger hormones.
- **Exercise**: Combine this nutrition plan with 30 min moderate activity daily.
- **Stress management**: Practice meditation or deep breathing to reduce cortisol.
- **Regular checkups**: Monitor your health metrics with your doctor.

---
{MEDICAL_DISCLAIMER}
"""
        return plan


# Singleton agent instance
_agent_instance = None

def get_agent() -> NutritionAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = NutritionAgent()
    return _agent_instance
