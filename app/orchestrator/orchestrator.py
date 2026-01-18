import re
from copy import deepcopy
from app.orchestrator.state import OrchestratorState
from app.orchestrator.graph import build_graph
from app.agents.language_agent import LanguageVoiceAgent

import json
import os

SESSION_FILE = "sessions.json"

def load_sessions():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_sessions(sessions):
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump(sessions, f)
    except:
        pass

SESSION_STATE = load_sessions()
ACTIVE_LANGUAGE = {}

graph = build_graph()
voice_agent = LanguageVoiceAgent()
tamil_pattern = re.compile(r"[\u0B80-\u0BFF]")


def run_orchestrator(user_input: str = "", user_id: str = "default", **kwargs):
    """
    SESSION-AWARE ORCHESTRATOR (HARD FIXED)
    """

    # -----------------------------
    # 1️⃣ LOAD OR CREATE SESSION
    # -----------------------------
    if user_id in SESSION_STATE:
        state = deepcopy(SESSION_STATE[user_id])
    else:
        state: OrchestratorState = {
            "user_input": "",
            "language": None,
            "domain": None,
            "intent": None,
            "extracted_data": {},
            "workflow_step": None,
            "farmer_data": {},
            "current_agent": None,
            "next_steps": [],
            "voice_reply": None,
            "last_response": None
        }

    # Preserve last response for repetition logic
    if state.get("response"):
        state["last_response"] = state["response"]

    # -----------------------------
    # 2️⃣ HANDLE INPUT & LANGUAGE LOCK
    # -----------------------------
    # Detect language from current input
    if "audio_path" in kwargs:
        voice = voice_agent.speech_to_text(kwargs["audio_path"])
        text = voice["text"]
        detected_lang = voice["language"]
    else:
        text = user_input or ""
        detected_lang = "ta" if tamil_pattern.search(text) else "en"

    state["user_input"] = text

    # DYNAMIC LANGUAGE DETECTION
    if text.strip() or "audio_path" in kwargs:
        # Check for any Tamil characters
        has_tamil = bool(re.search(r"[\u0B80-\u0BFF]", text))
        if has_tamil or (state.get("language") == "ta" and not text.strip()):
            detected_lang = "ta"
        else:
            detected_lang = "en"
            
        state["language"] = detected_lang
        ACTIVE_LANGUAGE[user_id] = detected_lang
    elif state.get("language"):
        # Keep existing
        pass
    else:
         state["language"] = "en"
    
    # -----------------------------
    # 🔓 3.5 ESCAPE HATCH (Unlock Domain)
    # -----------------------------
    # Translation keys for help
    is_tamil = state.get("language") == "ta"

    # DEBUG
    print(f"DEBUG: Input='{text}', Detected='{detected_lang}', Final='{state.get('language')}'")
    # -----------------------------
    # 3️⃣ HANDLE TRANSIENT INPUTS (IMAGE/AUDIO)
    # -----------------------------
    # Clear old image/audio paths from state to prevent loops
    state["aadhaar_image"] = None
    
    for key, value in kwargs.items():
        if value is not None:
            state[key] = value   # ← Set image/audio ONLY for this request

    # -----------------------------
    # 🔓 4️⃣ ESCAPE HATCH (Unlock Domain)
    # -----------------------------
    # Check if user wants to switch context explicitly
    input_lower = state["user_input"].lower()
    
    educational_keywords = ["explain", "what is", "teach", "physics", "math", "science", "school", "scholarship", "support", "உதவித்தொகை", "கல்வி"]
    health_keywords = ["fever", "pain", "doctor", "hospital", "medicine", "symptom", "headache", "book", "appointment", "பதிவு", "மருத்துவமனை"]
    
    if any(k in input_lower for k in educational_keywords):
        state["domain"] = "education"
        state["intent"] = "learn"
        # CLEAR Governance State to prevent locking
        state["workflow_step"] = None
        state["aadhaar_image"] = None
        print("DEBUG: Domain Switch -> EDUCATION")

    elif any(k in input_lower for k in health_keywords):
        state["domain"] = "healthcare"
        state["intent"] = "consult"
        # CLEAR Governance State
        state["workflow_step"] = None
        state["aadhaar_image"] = None
        print("DEBUG: Domain Switch -> HEALTHCARE")

    # -----------------------------
    # 🔒 5️⃣ HARD WORKFLOW ENFORCEMENT (If no switch)
    # -----------------------------
    # Only enforce governance if we haven't just switched domains
    elif state.get("workflow_step") or state.get("aadhaar_image"):
        state["domain"] = "governance"
        state["intent"] = "apply"
        print("DEBUG: Enforcing Governance Workflow")

    # -----------------------------
    # 5️⃣ RUN GRAPH
    # -----------------------------
    result = graph.invoke(state)

    # -----------------------------
    # 6️⃣ SAVE SESSION (MERGE SAFE)
    # -----------------------------
    SESSION_STATE[user_id] = deepcopy(result)
    save_sessions(SESSION_STATE)
    result["current_agent"] = result.get("domain")

    return result
