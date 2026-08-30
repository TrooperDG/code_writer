import uuid

import streamlit as st
from streamlit_modules.graph_runner import inspect_graph_state
from streamlit_modules.ui_components import (
    render_action_bar,
    render_chat_history,
    render_current_response,
    render_streaming_thinking_area,
)

st.set_page_config(page_title="Code Generator Agent", layout="wide")
st.title("LangGraph Code Generator")

# 1. Initialize Session State
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "graph_running" not in st.session_state:
    st.session_state.graph_running = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_reasoning" not in st.session_state:
    st.session_state.current_reasoning = ""

config = {"configurable": {"thread_id": st.session_state.thread_id}}

# Sidebar Controls
st.sidebar.header("Configuration")
workspace_dir = st.sidebar.text_input("Workspace Directory", value="./output")

if st.sidebar.button("Clear / New Session"):
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.graph_running = False
    st.session_state.chat_history = []
    st.session_state.current_reasoning = ""
    st.rerun()

# 2. Render Existing Chat History
render_chat_history()

# 3. Check Current Graph State
current_state, is_interrupted, state_values = (
    inspect_graph_state(config) if st.session_state.graph_running else (None, False, {})
)

# 4. Handle Active Interrupt Display or Graph Completion
if is_interrupted:
    render_current_response(state_values)
elif st.session_state.graph_running and not is_interrupted:
    final_values = current_state.values if current_state else {}
    if final_values.get("is_write_success"):
        saved_msg = f"File successfully saved to `{final_values.get('workspace_dir')}/{final_values.get('file_name')}`"
        st.session_state.chat_history.append(
            {"role": "assistant", "content": saved_msg}
        )
    st.session_state.graph_running = False
    st.rerun()

# 5. Handle Inputs (Approve / Revise vs. New Prompt)
if is_interrupted:
    render_action_bar(state_values, config)
else:
    user_query = st.chat_input("What code would you like to generate?")

    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        st.session_state.graph_running = True
        st.session_state.current_reasoning = ""

        # Render the streaming thinking block live into UI
        render_streaming_thinking_area(user_query, workspace_dir, config)

        # Rerun to switch to the human_code_review interrupt view
        st.rerun()
