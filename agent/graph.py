from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END

from agent.state import CodingAgentState
from agent.nodes import generate_code, review_code, route_after_review, write_file


def build_graph():
    builder = StateGraph(CodingAgentState)

    builder.add_node("generate_code", generate_code)
    builder.add_node("review_code", review_code)
    builder.add_node("write_file", write_file)

    builder.add_edge(START, "generate_code")
    builder.add_edge("generate_code", "review_code")
    # builder.add_edge("review_code", END)

    builder.add_edge("write_file", END)

    builder.add_conditional_edges(
        "review_code",
        route_after_review,
        {
            "write_file": "write_file",
            "end": END,
        },
    )

    checkpointer = InMemorySaver()

    return builder.compile(checkpointer=checkpointer)


graph = build_graph()
