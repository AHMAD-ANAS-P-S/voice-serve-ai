from app.workflows.data_checker import missing_fields
from app.agents.governance_prompts import ask_aadhaar, ask_bank
from app.workflows.eligibility_engine import check_eligibility, eligibility_response


def governance_flow(state: dict) -> dict:
    language = state.get("language")
    farmer_data = state.get("farmer_data", {})
    step = state.get("workflow_step")

    missing = missing_fields(farmer_data)

    # Ask Aadhaar
    if "aadhaar" in missing:
        state["workflow_step"] = "aadhaar_required"
        return ask_aadhaar(language)

    # Ask Bank
    if "bank" in missing or "ifsc" in missing:
        state["workflow_step"] = "bank_required"
        return ask_bank(language)

    # Eligibility check
    eligible = check_eligibility(farmer_data)
    state["eligibility"] = eligible

    state["workflow_step"] = "confirm_submission"
    return {
        "response": eligibility_response(language, eligible),
        "next_steps": ["confirm_submission"]
    }
