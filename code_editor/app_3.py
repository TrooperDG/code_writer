import uuid
import streamlit as st
from graph import graph
from langgraph.types import Command
from state import FlowState

st.set_page_config(page_title="Code Generator Agent", layout="wide")
st.title("LangGraph Code Generator")

# 1. Initialize Session State
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "graph_running" not in st.session_state:
    st.session_state.graph_running = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

config = {"configurable": {"thread_id": st.session_state.thread_id}}

# Sidebar Controls
st.sidebar.header("Configuration")
workspace_dir = st.sidebar.text_input("Workspace Directory", value="./output")

if st.sidebar.button("Clear / New Session"):
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.graph_running = False
    st.session_state.chat_history = []
    st.rerun()

# 2. Render Existing Chat History
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "code" in msg:
            st.markdown(f"**Filename:** `{msg.get('file_name', 'code')}`")
            st.code(msg["code"], language="python")

# 3. Handle Initial Query Input
if not st.session_state.graph_running:
    user_query = st.chat_input("What code would you like to generate?")

    if user_query:
        # Add user prompt to history
        st.session_state.chat_history.append({"role": "user", "content": user_query})

        initial_state = FlowState(query=user_query, workspace_dir=workspace_dir)
        st.session_state.graph_running = True

        # Stream graph up to interrupt point
        for event in graph.stream(initial_state, config=config):
            pass
        st.rerun()

# 4. Active Interrupt & Review Interface inside Chat Flow
if st.session_state.graph_running:
    current_state = graph.get_state(config)

    # Check for active interrupt at human_code_review
    if current_state.tasks and len(current_state.tasks) > 0:
        task = current_state.tasks[0]
        if hasattr(task, "interrupts") and task.interrupts:
            state_values = current_state.values
            explanation = state_values.get("code_explanation", "")
            code_content = state_values.get("generated_code", "")
            file_name = state_values.get("file_name", "generated_code")

            # Render assistant payload in chat view
            with st.chat_message("assistant"):
                if explanation:
                    st.write(explanation)
                st.markdown(f"**Filename:** `{file_name}`")
                st.code(code_content, language="python")

                st.divider()
                st.markdown("### Code Review Required")

                # Action forms for user response
                with st.form("review_form"):
                    feedback_text = st.text_input(
                        "Revision Feedback (leave blank if approving)"
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        approve_btn = st.form_submit_button(
                            "Approve & Save", type="primary"
                        )
                    with col2:
                        reject_btn = st.form_submit_button("Request Changes")

                if approve_btn:
                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": explanation,
                            "code": code_content,
                            "file_name": file_name,
                        }
                    )
                    st.session_state.chat_history.append(
                        {"role": "user", "content": "Approved code for writing."}
                    )

                    approval_payload = {"approved": True, "feedback": ""}
                    for event in graph.stream(
                        Command(resume=approval_payload), config=config
                    ):
                        pass
                    st.rerun()

                elif reject_btn:
                    feedback_msg = feedback_text or "Needs revision."
                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": explanation,
                            "code": code_content,
                            "file_name": file_name,
                        }
                    )
                    st.session_state.chat_history.append(
                        {
                            "role": "user",
                            "content": f"Requested changes: {feedback_msg}",
                        }
                    )

                    approval_payload = {"approved": False, "feedback": feedback_msg}
                    for event in graph.stream(
                        Command(resume=approval_payload), config=config
                    ):
                        pass
                    st.rerun()

    else:
        # 5. Graph Finalization
        final_values = current_state.values
        if final_values.get("is_write_success"):
            saved_msg = f"File successfully written to `{final_values.get('workspace_dir')}/{final_values.get('file_name')}`"
            st.session_state.chat_history.append(
                {"role": "assistant", "content": saved_msg}
            )

        st.session_state.graph_running = False
        st.rerun()
