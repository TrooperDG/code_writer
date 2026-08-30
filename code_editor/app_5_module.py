# app.py
import uuid

import streamlit as st
from streamlit_modules.graph_runner import inspect_graph_state, run_initial_graph
from streamlit_modules.ui_components import (
    render_action_bar,
    render_chat_history,
    render_current_response,
)

st.set_page_config(page_title="Code Generator Agent", layout="wide")
st.title("LangGraph Code Generator")

# State Initialization
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "graph_running" not in st.session_state:
    st.session_state.graph_running = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

config = {"configurable": {"thread_id": st.session_state.thread_id}}

# Sidebar
st.sidebar.header("Configuration")
workspace_dir = st.sidebar.text_input("Workspace Directory", value="./output")
if st.sidebar.button("Clear / New Session"):
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.graph_running = False
    st.session_state.chat_history = []
    st.rerun()

# 1. Render History
render_chat_history()

# 2. Inspect Graph
current_state, is_interrupted, state_values = (
    inspect_graph_state(config) if st.session_state.graph_running else (None, False, {})
)

# 3. Handle Active Output / Completion
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

# 4. Handle Inputs
if is_interrupted:
    render_action_bar(state_values, config)
else:
    user_query = st.chat_input("What code would you like to generate?")
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        st.session_state.graph_running = True
        run_initial_graph(user_query, workspace_dir, config)
        st.rerun()
