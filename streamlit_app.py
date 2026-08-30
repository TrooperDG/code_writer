import uuid

import streamlit as st
from langgraph.types import Command

from agent.graph import graph


st.set_page_config(
    page_title="Coding Agent",
    page_icon="💻",
)


# --------------------------------------------------
# Session state initialization
# --------------------------------------------------

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "graph_result" not in st.session_state:
    st.session_state.graph_result = None

if "started" not in st.session_state:
    st.session_state.started = False


# --------------------------------------------------
# Page
# --------------------------------------------------

st.title("💻 Coding Agent")

user_request = st.text_area(
    "What code should I create?",
    placeholder="Create a JavaScript function to add 3 numbers",
)


# --------------------------------------------------
# Start generation
# --------------------------------------------------

if st.button("Generate Code", type="primary"):
    if not user_request.strip():
        st.warning("Please enter a coding request.")
    else:
        initial_state = {
            "user_request": user_request,
            "generated_code": "",
            "code_approved": False,
        }

        config = {
            "configurable": {
                "thread_id": st.session_state.thread_id,
            }
        }

        result = graph.invoke(
            initial_state,
            config=config,
        )

        st.session_state.graph_result = result
        st.session_state.started = True

        # st.rerun()


# --------------------------------------------------
# Display generated code
# --------------------------------------------------

result = st.session_state.graph_result

if result and "__interrupt__" in result:
    interrupt = result["__interrupt__"][0]

    interrupt_value = interrupt.value

    if interrupt_value["type"] == "code_review":
        st.subheader("Generated Code")

        st.code(
            interrupt_value["code"],
            language="javascript",
        )

        st.subheader("Do you approve this code?")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Approve", use_container_width=True):
                config = {
                    "configurable": {
                        "thread_id": st.session_state.thread_id,
                    }
                }

                result = graph.invoke(
                    Command(resume=True),
                    config=config,
                )

                st.session_state.graph_result = result

                st.rerun()

        with col2:
            if st.button("❌ Reject", use_container_width=True):
                config = {
                    "configurable": {
                        "thread_id": st.session_state.thread_id,
                    }
                }

                result = graph.invoke(
                    Command(resume=False),
                    config=config,
                )

                st.session_state.graph_result = result

                st.rerun()
