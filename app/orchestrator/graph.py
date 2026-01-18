from langgraph.graph import StateGraph
from app.orchestrator.state import OrchestratorState
from app.orchestrator.nodes.basic_nodes import input_node, simple_router
from app.orchestrator.nodes.intent_detector import intent_detector
from app.orchestrator.nodes.response_node import response_node


def build_graph():
    graph = StateGraph(OrchestratorState)

    graph.add_node("input", input_node)
    graph.add_node("router", simple_router)
    graph.add_node("intent", intent_detector)
    graph.add_node("response", response_node)

    graph.set_entry_point("input")

    graph.add_edge("input", "router")
    graph.add_edge("router", "intent")
    graph.add_edge("intent", "response")

    return graph.compile()
