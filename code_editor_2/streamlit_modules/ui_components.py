import streamlit as st

from .graph_runner import render_graph_streaming, resume_graph_with_approval


def render_chat_history():
    """Renders persistent message history, including reasoning blocks and code outputs."""
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            # Display past reasoning inside a collapsed expander
            if msg.get("reasoning"):
                with st.expander("💭 Thinking process", expanded=False):
                    st.write(msg["reasoning"])

            st.write(msg["content"])
            if "code" in msg:
                st.markdown(f"**Filename:** `{msg.get('file_name', 'code')}`")
                st.code(msg["code"], language="python")


def render_current_response(state_values: dict):
    """Renders the current response during a human review interrupt."""
    explanation = state_values.get("code_explanation", "")
    code_content = state_values.get("generated_code", "")
    file_name = state_values.get("file_name", "generated_code")
    reasoning = state_values.get("reasoning_content", "")

    with st.chat_message("assistant"):
        # Collapsible thinking block for the current turn
        if reasoning:
            with st.status("Finished thinking", expanded=False, state="complete"):
                st.markdown(reasoning)

        if explanation:
            st.write(explanation)
        st.markdown(f"**Filename:** `{file_name}`")
        st.code(code_content, language="python")


def render_streaming_thinking_area(query: str, workspace_dir: str, config: dict):
    """Container that live-streams thinking tokens into an active status block."""
    with st.chat_message("assistant"):
        with st.status("Thinking...", expanded=True, state="running") as status_box:
            render_graph_streaming(query, workspace_dir, config, status_box)
            status_box.update(
                label="Finished thinking", state="complete", expanded=False
            )


def render_action_bar(state_values: dict, config: dict):
    """Renders the top approval button and revision chat bar."""
    col_app, _ = st.columns([1, 4])
    explanation = state_values.get("code_explanation", "")
    code_content = state_values.get("generated_code", "")
    file_name = state_values.get("file_name", "generated_code")
    reasoning = state_values.get("reasoning_content", "")

    # Approve Button
    with col_app:
        if st.button("✓ Approve & Save", type="primary", use_container_width=True):
            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": explanation,
                    "code": code_content,
                    "file_name": file_name,
                    "reasoning": reasoning,
                }
            )
            st.session_state.chat_history.append(
                {"role": "user", "content": "Approved code for saving."}
            )
            resume_graph_with_approval(True, "", config)
            st.rerun()

    # Revision Input Bar
    revision_feedback = st.chat_input(placeholder="Write feedback here to revise...")
    if revision_feedback:
        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": explanation,
                "code": code_content,
                "file_name": file_name,
                "reasoning": reasoning,
            }
        )
        st.session_state.chat_history.append(
            {"role": "user", "content": f"Revise: {revision_feedback}"}
        )
        resume_graph_with_approval(False, revision_feedback, config)
        st.rerun()
