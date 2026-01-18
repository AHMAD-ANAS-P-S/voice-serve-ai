from app.llm.ai_responder import ai_responder
from app.config import settings
import re
import requests

class EducationAgent:
    """
    Education Agent with Scholarship Workflow.
    """
    def handle(self, state: dict) -> dict:
        user_text = state.get("user_input", "").lower()
        language = state.get("language", "en")
        step = state.get("workflow_step")
        state.setdefault("education_data", {})
        data = state["education_data"]

        is_tamil = language == "ta"

        # -----------------------------
        # SCHOLARSHIP WORKFLOW
        # -----------------------------
        if any(w in user_text for w in ["scholarship", "apply", "support", "money for studies", "உதவித்தொகை"]):
            state["workflow_step"] = "edu_name_required"
            state["response"] = "தேசிய கல்வி உதவித்தொகைக்கு விண்ணப்பிப்போம். மாணவர் பெயர் என்ன?" if is_tamil else "Let's apply for the National Scholarship. What is the student's full name?"
            return state

        if step == "edu_name_required":
            data["name"] = user_text
            state["workflow_step"] = "edu_aadhaar_required"
            state["response"] = "நன்றி. உங்கள் ஆதார் எண்ணைச் சொல்லுங்கள்." if is_tamil else "Thank you. Please tell me your Aadhaar number."
            self.sync_to_portal(data)
            return state

        if step == "edu_aadhaar_required":
            clean_num = re.sub(r"[^0-9]", "", user_text)
            if len(clean_num) == 12:
                data["aadhaar"] = clean_num
                state["workflow_step"] = "edu_mobile_required"
                state["response"] = "சரி. உங்கள் மொபைல் எண் என்ன?" if is_tamil else "Got it. What is your mobile number?"
            else:
                state["response"] = "சரியான 12 இலக்க ஆதார் எண்ணை வழங்கவும்." if is_tamil else "Please provide a valid 12-digit Aadhaar number."
            self.sync_to_portal(data)
            return state

        if step == "edu_mobile_required":
            clean_num = re.sub(r"[^0-9]", "", user_text)
            if len(clean_num) >= 10:
                data["mobile"] = clean_num
                state["workflow_step"] = "edu_school_required"
                state["response"] = "நீங்கள் எந்தப் பள்ளியில் அல்லது கல்லூரியில் படிக்கிறீர்கள்?" if is_tamil else "Which school or college do you study in?"
            else:
                state["response"] = "சரியான மொபைல் எண்ணை வழங்கவும்." if is_tamil else "Please provide a valid mobile number."
            self.sync_to_portal(data)
            return state

        if step == "edu_school_required":
            data["institution"] = user_text
            state["workflow_step"] = "edu_grade_required"
            state["response"] = "நீங்கள் எந்த வகுப்பில் இருக்கிறீர்கள்?" if is_tamil else "And which grade or year are you in?"
            self.sync_to_portal(data)
            return state

        if step == "edu_grade_required":
            data["grade"] = user_text
            state["workflow_step"] = "edu_confirm"
            state["response"] = f"சிறப்பு! பெயர்: {data.get('name')}, கல்வி நிறுவனம்: {data.get('institution')}. விண்ணப்பிக்க YES என்று சொல்லுங்கள்." if is_tamil else f"Great! Name: {data.get('name')}, School: {data.get('institution')}. Say YES to submit application."
            self.sync_to_portal(data)
            return state

        if step == "edu_confirm":
            if any(w in user_text for w in ["yes", "submit", "aama", "sari", "confirm"]):
                # Submit to portal
                self.sync_to_portal({**data, "submitted": True, "active_scheme": "Scholarship", "receipt_id": "EDU-" + user_text[:3].upper()})
                state["workflow_step"] = "completed"
                state["response"] = "விண்ணப்பம் வெற்றிகரமாக சமர்ப்பிக்கப்பட்டது! உங்களுக்கு ஒரு SMS வரும்." if is_tamil else "Application Submitted Successfully! You will receive an SMS update."
                return state

        # Default Education Response (LLM)
        query = f"Explain this educational concept clearly: {user_text}"
        llm_result = ai_responder(query, language)
        return {
            "response": llm_result.get("response", "I'm here to help with your studies."),
            "next_steps": []
        }

    def sync_to_portal(self, data: dict):
        try:
            requests.post(f"{settings.MOCK_PORTAL_URL}/update_state", json=data, timeout=1)
        except:
            pass
