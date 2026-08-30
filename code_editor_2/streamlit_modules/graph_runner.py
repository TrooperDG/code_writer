import asyncio
from graph import graph
from langgraph.types import Command
from state import FlowState


async def stream_graph_status(input_state, config: dict, status_container):
    thinking_text = ""
    status_container.markdown("Preparing your request...")

    # Stream graph events
    async for event in graph.astream_events(input_state, config=config, version="v2"):
        kind = event["event"]
        node_name = event.get("metadata", {}).get("langgraph_node")

        if kind == "on_chain_start" and node_name == "generate_code":
            status_container.update(
                label="Thinking through the code...", state="running", expanded=True
            )
        elif kind == "on_chain_start" and node_name == "human_code_review":
            status_container.update(
                label="Preparing code review...", state="running", expanded=True
            )

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

    return thinking_text


async def run_initial_graph_streaming(
    query: str, workspace_dir: str, config: dict, status_container
):
    initial_state = FlowState(query=query, workspace_dir=workspace_dir)
    return await stream_graph_status(initial_state, config, status_container)


async def run_resume_graph_streaming(
    approved: bool, feedback: str, config: dict, status_container
):
    approval_payload = {"approved": approved, "feedback": feedback}
    return await stream_graph_status(
        Command(resume=approval_payload), config, status_container
    )


def render_graph_streaming(query: str, workspace_dir: str, config: dict, status_box):
    """Bridge async streaming to synchronous Streamlit runs."""
    return asyncio.run(
        run_initial_graph_streaming(query, workspace_dir, config, status_box)
    )


def render_resume_graph_streaming(
    approved: bool, feedback: str, config: dict, status_box
):
    """Bridge async graph resume streaming to synchronous Streamlit runs."""
    return asyncio.run(
        run_resume_graph_streaming(approved, feedback, config, status_box)
    )


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
