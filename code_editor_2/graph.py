from langgraph.checkpoint.memory import InMemorySaver

from langgraph.graph import END, START, StateGraph
from nodes import generate_code, human_code_review, route_after_review, write_file
from state import FlowState


def build_graph():
    builder = StateGraph(FlowState)

    builder.add_node("generate_code", generate_code)
    builder.add_node("human_code_review", human_code_review)
    builder.add_node("write_file", write_file)
    #
    builder.add_edge(START, "generate_code")
    builder.add_edge("generate_code", "human_code_review")

    builder.add_conditional_edges("human_code_review", route_after_review)

    builder.add_edge("write_file", END)

    return builder.compile(checkpointer=InMemorySaver())


graph = build_graph()
