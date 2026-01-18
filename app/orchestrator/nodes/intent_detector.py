from app.orchestrator.state import OrchestratorState


def intent_detector(state: OrchestratorState) -> OrchestratorState:
    """
    Intent detector.
    MUST NOT run during active workflows.
    """

    # 🔒 DO NOT classify intent if document is present
    if state.get("aadhaar_image"):
        state["domain"] = "governance"
        state["intent"] = "apply"
        return state

    # 🔒 HARD WORKFLOW LOCK
    if state.get("workflow_step"):
        # DO NOT touch domain or intent
        return state

    text = state.get("user_input", "").lower()

    # -------------------------
    # REPETITION CHECK
    # -------------------------
    if any(w in text for w in ["repeat", "again", "thirumba", "marubadiyum"]):
        state["intent"] = "repeat"
        return state

    # -------------------------
    # DOMAIN DETECTION
    # -------------------------
    if any(w in text for w in ["kisan", "pm kisan", "farmer", "scheme", "apply", "subsidy"]):
        state["domain"] = "governance"
    elif any(w in text for w in ["fever", "doctor", "hospital", "health", "medicine"]):
        state["domain"] = "healthcare"
    else:
        state["domain"] = "education"

    # -------------------------
    # INTENT DETECTION
    # -------------------------
    if any(w in text for w in ["apply", "submit", "register"]):
        state["intent"] = "apply"
    elif any(w in text for w in ["check", "status"]):
        state["intent"] = "check"
    else:
        state["intent"] = "learn"

    state["extracted_data"] = {}
    return state
