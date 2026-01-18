from app.agents.education_agent import EducationAgent
from app.agents.healthcare_agent import HealthcareAgent
from app.agents.governance_agent import GovernanceAgent
from app.voice.tts import text_to_speech

education_agent = EducationAgent()
healthcare_agent = HealthcareAgent()
governance_agent = GovernanceAgent()


def response_node(state: dict) -> dict:
    """
    FINAL RESPONSE NODE
    HARD workflow ownership enforcement
    """

    # 🔒 ABSOLUTE RULE:
    # If workflow OR Aadhaar image exists → governance only
    if state.get("workflow_step") or state.get("aadhaar_image"):
        result = governance_agent.handle(state)

    else:
        domain = state.get("domain")
        intent = state.get("intent")

        if intent == "repeat":
             result = {
                 "response": state.get("last_response", "Sorry, I have nothing to repeat."),
                 "next_steps": []
             }
        elif domain == "education":
            result = education_agent.handle(state)
        elif domain == "healthcare":
            result = healthcare_agent.handle(state)
        elif domain == "governance":
            result = governance_agent.handle(state)
        else:
            result = {
                "response": "Sorry, I couldn’t understand your request.",
                "next_steps": []
            }

    # Normalize
    state["response"] = result.get("response", "")
    state["next_steps"] = result.get("next_steps", [])

    # Voice (never crash)
    try:
        state["voice_reply"] = text_to_speech(
            state["response"],
            state.get("language", "en")
        )
    except Exception:
        state["voice_reply"] = None

    return state
