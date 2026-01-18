from app.orchestrator.state import OrchestratorState


def input_node(state: dict) -> dict:
    return state


def simple_router(state: dict) -> dict:
    """
    Router with HARD workflow enforcement.
    """

    # 🔒 HARD LOCK: workflow owns routing
    if state.get("workflow_step"):
        state["domain"] = "governance"
        state["intent"] = "apply"
        return state

    # Default routing when no workflow
    if not state.get("domain"):
        state["domain"] = "education"

    return state

