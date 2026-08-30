# graph_runner.py
from graph import graph
from langgraph.types import Command
from state import FlowState


def run_initial_graph(query: str, workspace_dir: str, config: dict):
    initial_state = FlowState(query=query, workspace_dir=workspace_dir)
    for _ in graph.stream(initial_state, config=config):
        pass


def resume_graph_with_approval(approved: bool, feedback: str, config: dict):
    approval_payload = {"approved": approved, "feedback": feedback}
    for _ in graph.stream(Command(resume=approval_payload), config=config):
        pass


def inspect_graph_state(config: dict):
    current_state = graph.get_state(config)
    is_interrupted = False
    state_values = {}

    if current_state and current_state.tasks and len(current_state.tasks) > 0:
        task = current_state.tasks[0]
        if hasattr(task, "interrupts") and task.interrupts:
            is_interrupted = True
            state_values = current_state.values

    return current_state, is_interrupted, state_values
