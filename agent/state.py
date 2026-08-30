from typing import TypedDict


class CodingAgentState(TypedDict):
    user_request: str
    generated_code: str

    directory: str
    file_name: str

    code_approved: bool
    file_written: bool
