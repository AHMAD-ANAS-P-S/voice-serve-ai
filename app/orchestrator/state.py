from typing import TypedDict, Optional, Dict, List


class OrchestratorState(TypedDict):
    # 🗣 User input
    user_input: str
    language: Optional[str]

    # 🧠 Understanding
    domain: Optional[str]
    intent: Optional[str]
    extracted_data: Dict

    # 🔁 Agent routing
    current_agent: Optional[str]

    # 🧩 GOVERNANCE WORKFLOW MEMORY (VERY IMPORTANT)
    workflow_step: Optional[str]      # e.g. aadhaar_required, bank_required
    farmer_data: Dict                 # aadhaar, bank, land, name
    aadhaar_image: Optional[str]      # Path to uploaded image
    eligibility: Optional[bool]
    eligibility_checked: Optional[bool]
    receipt_id: Optional[str]

    # 💬 Output
    response: Optional[str]
    next_steps: List[str]

    # 🔊 Voice output (TTS)
    voice_reply: Optional[str]
    
    # Repetition Memory
    last_response: Optional[str]
