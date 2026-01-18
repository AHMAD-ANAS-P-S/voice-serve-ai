from app.workflows.pm_kisan_submit import submit_pm_kisan
from app.ocr.aadhaar_ocr import extract_aadhaar_data
from app.workflows.data_checker import missing_fields
from app.workflows.eligibility_engine import check_eligibility, eligibility_response
from app.workflows.reminders import schedule_pm_kisan_reminder
from app.llm.ai_responder import ai_responder
from app.config import settings
import re
import requests

class GovernanceAgent:
    """
    PM-Kisan workflow.
    DYNAMIC, ROBUST, NO-PREBUILT-DATA, AUTO-FORWARDING & PORTAL SYNC.
    """

    def handle(self, state: dict) -> dict:
        intent = state.get("intent")
        step = state.get("workflow_step")
        language = state.get("language", "en")
        user_text = state.get("user_input", "").lower().strip()
        
        state.setdefault("farmer_data", {})
        data = state["farmer_data"]

        # -----------------------------
        # 0. CHECK FOR "RESTART" OR "NEW"
        # -----------------------------
        if any(w in user_text for w in ["restart", "new", "start again"]):
            state["workflow_step"] = None
            state["farmer_data"] = {}
            state["eligibility_checked"] = False
            return self.ask_aadhaar(state)

        # -----------------------------
        # 1. CAPTURE DATA (Voice/Text)
        # -----------------------------
        if user_text:
            self.capture_voice_data(state, user_text)

        # -----------------------------
        # 2. PROCESS IMAGE (If sent)
        # -----------------------------
        if state.get("aadhaar_image"):
            ocr_result = extract_aadhaar_data(state["aadhaar_image"])
            # Update farmer data with what we found (No prebuilt fallback!)
            if ocr_result:
                data.update({
                    "name": ocr_result.get("name", data.get("name")),
                    "aadhaar": ocr_result.get("aadhaar", data.get("aadhaar")),
                    "dob": ocr_result.get("dob", data.get("dob")),
                    "gender": ocr_result.get("gender", data.get("gender")),
                    "pincode": ocr_result.get("pincode", data.get("pincode"))
                })
            # Sync to portal immediately
            self.sync_to_portal(data)
            # IMPORTANT: Clear image so it's not processed again
            state["aadhaar_image"] = None

        # -----------------------------
        # 3. ROUTE TO NEXT TASK
        # -----------------------------
        # Sync current data to portal
        self.sync_to_portal(data)

        # Start command?
        if intent == "apply" and not step:
            state["workflow_step"] = "aadhaar_required"

        # Check what is missing
        missing = missing_fields(data)

        if "aadhaar" in missing or "name" in missing:
            # If we don't even have a name/aadhaar, we usually ask for the upload
            if not data.get("aadhaar"):
                return self.ask_aadhaar(state)
            elif not data.get("name"):
                state["workflow_step"] = "name_required"
                state["response"] = "I couldn't read your name from the card. Please tell me your full name." if language == "en" else "ஆதாரில் இருந்து பெயரைப் படிக்க முடியவில்லை. உங்கள் முழு பெயரைச் சொல்லுங்கள்."
                return state

        if "mobile" in missing:
            state["workflow_step"] = "mobile_required"
            state["response"] = (
                "ஆதார் சரிபார்க்கப்பட்டது! உங்கள் மொபைல் எண்ணை கூறுங்கள்."
                if language == "ta" else "Aadhaar verified! Please provide your Mobile Number."
            )
            return state

        if "bank" in missing:
            state["workflow_step"] = "bank_required"
            state["response"] = (
                "உங்கள் வங்கி கணக்கு எண்ணைச் சொல்லுங்கள்."
                if language == "ta" else "Please tell me your Bank Account number."
            )
            return state

        if "ifsc" in missing:
            state["workflow_step"] = "ifsc_required"
            state["response"] = (
                "வங்கியின் IFSC குறியீட்டைச் சொல்லுங்கள்."
                if language == "ta" else "Please provide the IFSC code for your bank."
            )
            return state
            
        if "land" in missing:
            state["workflow_step"] = "land_required"
            state["response"] = (
                "உங்கள் நிலத்தின் விவரங்களை (ஏக்கரில்) சொல்லுங்கள்."
                if language == "ta" else "How many acres of land do you have?"
            )
            return state

        # All data collected! Check eligibility if not done
        if not state.get("eligibility_checked"):
            eligible = check_eligibility(data)
            state["eligibility"] = eligible
            state["eligibility_checked"] = True
            
            e_msg = eligibility_response(language, eligible)
            
            if not eligible:
                state["response"] = e_msg
                state["workflow_step"] = "rejected"
                return state
            
            # Move to confirmation
            summary = self.get_summary(state)
            state["response"] = f"{e_msg}\n\n{summary}"
            state["workflow_step"] = "confirm_submission"
            return state

        # -----------------------------
        # 4. CONFIRMATION STEP
        # -----------------------------
        if step == "confirm_submission":
            yes_patterns = ["yes", "yep", "ya", "submit", "confirm", "ok", "aama", "sari", "check"]
            if any(w in user_text for w in yes_patterns):
                return self.submit_application(state)
            else:
                summary = self.get_summary(state)
                state["response"] = f"Please confirm your details.\n\n{summary}"
                return state

        # Final Fallback
        ai_resp = ai_responder(user_text, language)
        state["response"] = ai_resp.get("response", "I'm ready. What would you like to do next?")
        return state

    def ask_aadhaar(self, state: dict) -> dict:
        state["response"] = (
            "PM-Kisan திட்டத்திற்கு விண்ணப்பிக்க, உங்கள் ஆதார் அட்டையின் புகைப்படத்தை அனுப்பவும்."
            if state["language"] == "ta" else "To apply for PM-Kisan, please upload your Aadhaar card image."
        )
        return state

    def get_summary(self, state: dict) -> str:
        d = state["farmer_data"]
        header = "📝 **விண்ணப்ப விவரங்கள் (Application Summary)**" if state["language"] == "ta" else "📝 **Application Summary**"
        lines = [
            f"👤 Name: {d.get('name')}",
            f"🆔 Aadhaar: {d.get('aadhaar')}",
            f"📱 Mobile: {d.get('mobile')}",
            f"🏦 Bank: {d.get('bank')}",
            f"🔑 IFSC: {d.get('ifsc')}",
            f"🚜 Land: {d.get('land')} Acres"
        ]
        footer = "\nசமர்ப்பிக்க **YES** என்று சொல்லுங்கள் (Say **YES** to submit)." 
        return f"{header}\n" + "\n".join(lines) + footer

    def submit_application(self, state: dict) -> dict:
        # PUSH to Portal state as "submitted"
        sub_data = dict(state["farmer_data"])
        sub_data["submitted"] = True
        self.sync_to_portal(sub_data)
        
        # Actuall call the submission workflow
        result = submit_pm_kisan(state["farmer_data"])
        receipt = result["receipt_id"]
        reminder = schedule_pm_kisan_reminder(receipt)

        state["workflow_step"] = "completed"
        state["eligibility_checked"] = False 
        
        state["response"] = (
            f"✅ **விண்ணப்பம் சமர்ப்பிக்கப்பட்டது!**\n\n"
            f"விண்ணப்ப எண் (ID): {receipt}\n"
            f"அடுத்த தவணை நினைவூட்டல்: {reminder['reminder_date']}\n\n"
            "நன்றி!"
            if state["language"] == "ta" else
            f"✅ **Application Submitted Successfully!**\n\n"
            f"Receipt ID: {receipt}\n"
            f"Next Installment Reminder: {reminder['reminder_date']}\n\n"
            "Thank you!"
        )
        return state

    def sync_to_portal(self, data: dict):
        try:
            requests.post(f"{settings.MOCK_PORTAL_URL}/update_state", json=data, timeout=1)
        except:
            pass

    def capture_voice_data(self, state: dict, text: str):
        data = state["farmer_data"]
        step = state.get("workflow_step")
        
        # Context-based capture
        if step == "name_required":
            data["name"] = text
            return

        # Clean text for digits only for numbers
        clean_num = re.sub(r"[^0-9]", "", text)
        
        # Mobile (10-12 digits)
        if len(clean_num) == 10 or (len(clean_num) == 12 and clean_num.startswith("91")):
            data["mobile"] = clean_num
            
        # Bank (12-18 digits)
        if len(clean_num) >= 11 and len(clean_num) <= 18 and clean_num != data.get("mobile"):
            data["bank"] = clean_num

        # IFSC (11 AlphaNum)
        ifsc_match = re.search(r"([a-z]{4}0[a-z0-9]{6})", text.replace(" ", ""), re.IGNORECASE)
        if ifsc_match:
            data["ifsc"] = ifsc_match.group(1).upper()
            
        # Land Details (e.g. "I have 5 acres" or "5.5")
        if "acre" in text.lower() or step == "land_required":
             land_match = re.search(r"(\d+\.?\d*)", text)
             if land_match:
                 data["land"] = land_match.group(1)
