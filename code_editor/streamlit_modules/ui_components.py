# ui_components.py
import streamlit as st

from .graph_runner import resume_graph_with_approval


def render_chat_history():
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "code" in msg:
                st.markdown(f"**Filename:** `{msg.get('file_name', 'code')}`")
                st.code(msg["code"], language="python")


def render_current_response(state_values: dict):
    explanation = state_values.get("code_explanation", "")
    code_content = state_values.get("generated_code", "")
    file_name = state_values.get("file_name", "generated_code")

    with st.chat_message("assistant"):
        if explanation:
            st.write(explanation)
        st.markdown(f"**Filename:** `{file_name}`")
        st.code(code_content, language="python")


def render_action_bar(state_values: dict, config: dict):
    col_app, _ = st.columns([1, 4])
    explanation = state_values.get("code_explanation", "")
    code_content = state_values.get("generated_code", "")
    file_name = state_values.get("file_name", "generated_code")

    # Approve Button
    with col_app:
        if st.button("✓ Approve & Save", type="primary", use_container_width=True):
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
            resume_graph_with_approval(True, "", config)
            st.rerun()

    # Revision Input
    revision_feedback = st.chat_input(placeholder="Write feedback here to revise...")
    if revision_feedback:
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
        resume_graph_with_approval(False, revision_feedback, config)
        st.rerun()
