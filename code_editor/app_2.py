import uuid
import streamlit as st
from graph import graph
from langgraph.types import Command
from state import FlowState

st.set_page_config(page_title="Code Generator Agent", layout="wide")
st.title("LangGraph Code Generator with Human Review")

# Initialize Session State
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "graph_running" not in st.session_state:
    st.session_state.graph_running = False

config = {"configurable": {"thread_id": st.session_state.thread_id}}

# Sidebar Settings
st.sidebar.header("Configuration")
workspace_dir = st.sidebar.text_input("Workspace Directory", value="./output")

# Input Form for New Query
if not st.session_state.graph_running:
    with st.form("query_form"):
        query = st.text_area("What code do you want to generate?", height=100)
        submitted = st.form_submit_button("Generate Code")

    if submitted and query:
        initial_state = FlowState(query=query, workspace_dir=workspace_dir)
        st.session_state.graph_running = True

        # Start graph execution up to the interrupt
        for event in graph.stream(initial_state, config=config):
            pass
        st.rerun()

# Check Graph State for Interrupts or Completion
if st.session_state.graph_running:
    current_state = graph.get_state(config)

    # Check if graph hit human_code_review interrupt
    if current_state.tasks and len(current_state.tasks) > 0:
        task = current_state.tasks[0]
        if hasattr(task, "interrupts") and task.interrupts:
            interrupt_data = task.interrupts[0].value

            st.subheader("Generated Code Review")
            state_values = current_state.values

            if state_values.get("code_explanation"):
                st.markdown("**Explanation:**")
                st.write(state_values.get("code_explanation"))

            file_name = state_values.get("file_name", "generated_code")
            code_content = state_values.get("generated_code", "")

            st.markdown(f"**Filename:** `{file_name}`")
            st.code(code_content, language="python")

            st.divider()

            # Review Action Form
            with st.form("review_form"):
                st.markdown("### Approve or Request Changes")
                feedback_text = st.text_input(
                    "Feedback / Change Request (leave empty if approving)"
                )

                col1, col2 = st.columns(2)
                with col1:
                    approve_btn = st.form_submit_button(
                        "Approve & Save File", type="primary"
                    )
                with col2:
                    reject_btn = st.form_submit_button("Request Revision")

            if approve_btn:
                # Resume execution with approval
                approval_payload = {"approved": True, "feedback": ""}
                for event in graph.stream(
                    Command(resume=approval_payload), config=config
                ):
                    pass
                st.rerun()

            elif reject_btn:
                # Resume execution with rejection feedback
                approval_payload = {
                    "approved": False,
                    "feedback": feedback_text or "Needs revision",
                }
                for event in graph.stream(
                    Command(resume=approval_payload), config=config
                ):
                    pass
                st.rerun()

    else:
        # Workflow Finished
        st.success("Workflow completed successfully!")

        final_values = current_state.values
        if final_values.get("is_write_success"):
            st.balloons()
            st.info(
                f"File saved to `{final_values.get('workspace_dir')}/{final_values.get('file_name')}`"
            )

        if st.button("Start New Workflow"):
            st.session_state.thread_id = str(uuid.uuid4())
            st.session_state.graph_running = False
            st.rerun()
