import asyncio
from graph import graph
from langgraph.types import Command
from state import FlowState


async def run_initial_graph_streaming(
    query: str, workspace_dir: str, config: dict, status_container
):
    initial_state = FlowState(query=query, workspace_dir=workspace_dir)
    thinking_text = ""

    # Stream graph events
    async for event in graph.astream_events(initial_state, config=config, version="v2"):
        kind = event["event"]

        # Stream LLM tokens in real-time
        if kind == "on_chat_model_stream":
            chunk = event["data"]["chunk"]

            # Extract thinking content from metadata/chunk
            reasoning_chunk = getattr(
                chunk,
                "reasoning_content",
                chunk.additional_kwargs.get("reasoning_content", ""),
            )

            if reasoning_chunk:
                thinking_text += reasoning_chunk
                status_container.markdown(thinking_text)


def render_graph_streaming(query: str, workspace_dir: str, config: dict, status_box):
    """Bridge async streaming to synchronous Streamlit runs."""
    asyncio.run(run_initial_graph_streaming(query, workspace_dir, config, status_box))


def resume_graph_with_approval(approved: bool, feedback: str, config: dict):
    """Resume graph execution when human approves or rejects code."""
    approval_payload = {"approved": approved, "feedback": feedback}
    for _ in graph.stream(Command(resume=approval_payload), config=config):
        pass


def inspect_graph_state(config: dict):
    """Inspect current checkpointer state for active interrupts or values."""
    current_state = graph.get_state(config)
    is_interrupted = False
    state_values = {}

    if current_state and current_state.tasks and len(current_state.tasks) > 0:
        task = current_state.tasks[0]
        if hasattr(task, "interrupts") and task.interrupts:
            is_interrupted = True
            state_values = current_state.values

    return current_state, is_interrupted, state_values
