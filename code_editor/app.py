import uuid
import streamlit as st
from langgraph.types import Command

from graph import graph

st.set_page_config(
    page_title="Coding Agent",
    page_icon="🤖",
)


# session state---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []


st.title("🤖 Coding Agent")

# -----------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
