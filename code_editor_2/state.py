from pydantic import BaseModel


class FlowState(BaseModel):
    # User query--
    query: str = ""
    workspace_dir: str = ""
    file_name: str = ""

    # code_generator ---
    generated_code: str = ""
    code_explanation: str = ""
    reasoning_content: str = ""
    generated_code_feedback: str = ""
    generated_code_approve: bool = False

    # file_writer---
    write_approve: bool = False
    is_write_success: bool = False
