from langchain_ollama import ChatOllama
from langgraph.types import interrupt
from pathlib import Path
from agent.state import CodingAgentState

llm = ChatOllama(
    model="qwen3:8b",
    temperature=0.3,
)


def generate_code(state: CodingAgentState) -> dict:
    """
    Generate source code from the user's request.
    """

    user_request = state["user_request"]

    prompt = f"""
        You are a professional software engineer.

        Generate the code requested by the user.

        User request:
          {user_request}

        Requirements:
        - Return only the source code.
        - Do not use Markdown code fences.
        - Do not explain the code.
        - Write production-quality code where appropriate.
        """

    response = llm.invoke(prompt)

    return {"generated_code": response.content}


def review_code(state: CodingAgentState) -> dict:
    """
    Pause execution and ask the human to review the generated code.
    """

    decision = interrupt(
        {
            "type": "code_review",
            "code": state["generated_code"],
        }
    )

    return {"code_approved": decision}


def write_file(state: CodingAgentState) -> dict:
    directory = Path(state["directory"])
    file_name = state["file_name"]

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = directory / file_name

    file_path.write_text(
        state["generated_code"],
        encoding="utf-8",
    )

    return {
        "file_written": True,
    }


# Routers-------------------------------
def route_after_review(state: CodingAgentState) -> str:
    if state["code_approved"]:
        return "write_file"

    return "end"
