from state import FlowState
from llm import structured_coder_llm
from langchain_core.prompts import ChatPromptTemplate
from langgraph.types import interrupt
from models import CodeApproval
from pathlib import Path

from typing import Literal


def generate_code(state: FlowState) -> dict:
    """
    Generate source code from the user's request.
    """

    query = state.query

    feedback = f" .Also, I provided this feedback on your previously generated code - please adress it : {state.generated_code_feedback}"

    if not state.generated_code_feedback:
        feedback = ""

    print("generate-", feedback)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a professional software engineer.

                Your task is to respond to the user request by returning a structured JSON output with two distinct parts:

                1. `generated_code`: Put ONLY raw, production-quality code here. Do NOT include markdown code fences (```), backticks, language tags, or introductory text.

                2. `code_explanation`: Put your short explanation, rationale, and any conversational text here. Never leak prose into `generated_code`.

                3. `file_name`: A valid filename with the correct file extension based on the programming language used (e.g., `.js`, `.py`, `.cpp`).
              
                """,
            ),
            ("human", "{query} {feedback}"),
        ]
    )

    chain = prompt | structured_coder_llm

    result = chain.invoke({"query": query, "feedback": feedback})

    return {
        "generated_code_feedback": "",
        "generated_code": result.generated_code,
        "code_explanation": result.code_explanation,
        "file_name": result.file_name,
    }


def human_code_review(state: FlowState) -> dict:
    approval: CodeApproval = interrupt(
        {"stage": "code_review", "code": state.generated_code}
    )

    isApproved = approval.get("approved", False)
    feedback = approval.get("feedback", "").strip()

    print(isApproved, feedback)

    if isApproved:
        feedback = ""

    # if not isApproved and not feedback:
    #     isApproved = True

    return {"generated_code_feedback": feedback, "generated_code_approve": isApproved}


def write_file(state: FlowState) -> dict:
    directory = Path(state.workspace_dir)
    file_name = state.file_name

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = directory / file_name

    file_path.write_text(
        state.generated_code,
        encoding="utf-8",
    )

    return {"is_write_success": True}


# ----------ROUTER-----------------
def route_after_review(state: FlowState) -> Literal["write_file", "generate_code"]:
    print("router", state.generated_code_approve)
    if state.generated_code_approve:
        return "write_file"

    return "generate_code"
