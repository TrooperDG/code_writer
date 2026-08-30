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

# 3. Check current graph state
current_state = graph.get_state(config) if st.session_state.graph_running else None
is_interrupted = False
state_values = {}

if current_state and current_state.tasks and len(current_state.tasks) > 0:
    task = current_state.tasks[0]
    if hasattr(task, "interrupts") and task.interrupts:
        is_interrupted = True
        state_values = current_state.values

# 4. Handle Interrupted Review Display (Assistant Message Output)
if is_interrupted:
    explanation = state_values.get("code_explanation", "")
    code_content = state_values.get("generated_code", "")
    file_name = state_values.get("file_name", "generated_code")

    with st.chat_message("assistant"):
        if explanation:
            st.write(explanation)
        st.markdown(f"**Filename:** `{file_name}`")
        st.code(code_content, language="python")

# 5. Handle Final State Completion
elif st.session_state.graph_running and not is_interrupted:
    final_values = current_state.values if current_state else {}
    if final_values.get("is_write_success"):
        saved_msg = f"File successfully saved to `{final_values.get('workspace_dir')}/{final_values.get('file_name')}`"
        st.session_state.chat_history.append(
            {"role": "assistant", "content": saved_msg}
        )

    st.session_state.graph_running = False
    st.rerun()


# 6. Bottom Interaction Bar (Approve Button + Dynamic Input Bar)
if is_interrupted:
    # Approve Button directly on top of the input box
    col_app, _ = st.columns([1, 4])
    with col_app:
        if st.button("✓ Approve & Save", type="primary", use_container_width=True):
            explanation = state_values.get("code_explanation", "")
            code_content = state_values.get("generated_code", "")
            file_name = state_values.get("file_name", "generated_code")

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": explanation,
                    "code": code_content,
                    "file_name": file_name,
                }
            )
            st.session_state.chat_history.append(
                {"role": "user", "content": "Approved code for saving."}
            )

            approval_payload = {"approved": True, "feedback": ""}
            for event in graph.stream(Command(resume=approval_payload), config=config):
                pass
            st.rerun()

    # Chat Input configured for Revisions
    revision_feedback = st.chat_input(placeholder="Write feedback here to revise...")

    if revision_feedback:
        explanation = state_values.get("code_explanation", "")
        code_content = state_values.get("generated_code", "")
        file_name = state_values.get("file_name", "generated_code")

        # Push previous assistant result & user feedback into persistent history
        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": explanation,
                "code": code_content,
                "file_name": file_name,
            }
        )
        st.session_state.chat_history.append(
            {"role": "user", "content": f"Revise: {revision_feedback}"}
        )

        approval_payload = {"approved": False, "feedback": revision_feedback}
        for event in graph.stream(Command(resume=approval_payload), config=config):
            pass
        st.rerun()

else:
    # Standard Input for New Queries
    user_query = st.chat_input("What code would you like to generate?")

    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        initial_state = FlowState(query=user_query, workspace_dir=workspace_dir)
        st.session_state.graph_running = True

        for event in graph.stream(initial_state, config=config):
            pass
        st.rerun()
