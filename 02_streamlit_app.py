import uuid

import streamlit as st
from langgraph.types import Command

from agent.graph import graph


st.set_page_config(
    page_title="Coding Agent",
    page_icon="💻",
)


if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "graph_result" not in st.session_state:
    st.session_state.graph_result = None


st.title("💻 Coding Agent")


user_request = st.text_area(
    "What code should I create?",
    placeholder="Create a JavaScript function to add 3 numbers",
)

directory = st.text_input(
    "Directory",
    placeholder="workspace/my_project",
)

file_name = st.text_input(
    "File name",
    placeholder="calculator.js",
)


if st.button(
    "Generate Code",
    type="primary",
):
    if not user_request.strip():
        st.warning("Please enter a coding request.")

    elif not directory.strip():
        st.warning("Please enter a directory.")

    elif not file_name.strip():
        st.warning("Please enter a file name.")

    else:
        initial_state = {
            "user_request": user_request,
            "generated_code": "",
            "directory": directory,
            "file_name": file_name,
            "code_approved": False,
            "file_written": False,
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

        st.write(f"**Directory:** `{directory}`")

        st.write(f"**File:** `{file_name}`")

        st.subheader("Do you approve this code?")

        col1, col2 = st.columns(2)

        config = {
            "configurable": {
                "thread_id": st.session_state.thread_id,
            }
        }

        with col1:
            if st.button(
                "✅ Approve",
                use_container_width=True,
            ):
                result = graph.invoke(
                    Command(resume=True),
                    config=config,
                )

                st.session_state.graph_result = result

                st.success("Code written successfully!")
                st.rerun()

        with col2:
            if st.button(
                "❌ Reject",
                use_container_width=True,
            ):
                result = graph.invoke(
                    Command(resume=False),
                    config=config,
                )

                st.session_state.graph_result = result

                st.warning("Code rejected.")


if result and result.get("file_written"):
    st.success("✅ File created successfully.")

    file_path = f"{result['directory']}/{result['file_name']}"

    st.write(f"**File:** `{file_path}`")
