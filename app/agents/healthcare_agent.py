from app.llm.ai_responder import ai_responder
from app.config import settings
import re
import requests

class HealthcareAgent:
    """
    Healthcare Agent with Hospital Booking Workflow.
    """
    def handle(self, state: dict) -> dict:
        user_text = state.get("user_input", "").lower()
        language = state.get("language", "en")
        step = state.get("workflow_step")
        state.setdefault("health_data", {})
        data = state["health_data"]

        is_tamil = language == "ta"

        # -----------------------------
        # BOOKING WORKFLOW
        # -----------------------------
        if any(w in user_text for w in ["book", "appointment", "doctor", "hospital", "booking", "பதிவு"]):
            state["workflow_step"] = "health_name_required"
            state["response"] = "அரசு மருத்துவமனையில் முன்பதிவு செய்ய முடியும். நோயாளியின் பெயர் என்ன?" if is_tamil else "I can book an appointment at the Government Hospital. What is the patient's name?"
            return state

        if step == "health_name_required":
            data["name"] = user_text
            state["workflow_step"] = "health_aadhaar_required"
            state["response"] = "நோயாளியின் பெயர் குறிக்கப்பட்டது. ஆதார் எண்ணைச் சொல்லுங்கள்." if is_tamil else "Patient name noted. Please share the Aadhaar number."
            self.sync_to_portal(data)
            return state

        if step == "health_aadhaar_required":
            clean_num = re.sub(r"[^0-9]", "", user_text)
            if len(clean_num) == 12:
                data["aadhaar"] = clean_num
                state["workflow_step"] = "health_symptoms_required"
                state["response"] = "உங்களுக்கு என்ன அறிகுறிகள் உள்ளன அல்லது எந்தத் துறை தேவை?" if is_tamil else "What are the symptoms or department you need?"
            else:
                state["response"] = "12 இலக்க ஆதார் எண்ணைச் சொல்லுங்கள்." if is_tamil else "Please tell me a 12-digit Aadhaar number."
            self.sync_to_portal(data)
            return state

        if step == "health_symptoms_required":
            data["symptoms"] = user_text
            state["workflow_step"] = "health_confirm"
            state["response"] = "அறிகுறிகள் குறிக்கப்பட்டன. முன்பதிவு செய்ய YES என்று சொல்லுங்கள்." if is_tamil else "Got the symptoms. Say YES to book the appointment."
            self.sync_to_portal(data)
            return state

        if step == "health_confirm":
            if any(w in user_text for w in ["yes", "submit", "aama", "sari", "confirm"]):
                self.sync_to_portal({**data, "submitted": True, "active_scheme": "Hospital"})
                state["workflow_step"] = "completed"
                state["response"] = "மருத்துவமனை முன்பதிவு முடிந்தது! பதிவு எண் உங்கள் மொபைலுக்கு வரும்." if is_tamil else "Hospital Appointment Fixed! Registration number sent to your phone."
                return state

        # Default Health Advice (LLM)
        query = f"Provide general medical guidance for: {user_text}. End with a disclaimer."
        result = ai_responder(query, language)
        return result

    def sync_to_portal(self, data: dict):
        try:
            requests.post(f"{settings.MOCK_PORTAL_URL}/update_state", json=data, timeout=1)
        except:
            pass
