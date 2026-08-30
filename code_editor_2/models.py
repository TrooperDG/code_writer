from pydantic import BaseModel, Field


class CodeStructure(BaseModel):
    generated_code: str = Field(
        description="ONLY the executable code snippet. DO NOT include backticks (```), language identifiers, introductory text, or Markdown formatting."
    )
    code_explanation: str = Field(
        description="A clear, short explanation of how the code works and any conversational responses."
    )
    file_name: str = Field(
        description="The filename with appropriate extension (e.g., 'main.py', 'script.js', 'index.html'). Use user's requested name if provided, otherwise derive a clean, snake_case or kebab-case name from the prompt."
    )


class CodeApproval(BaseModel):
    approved: bool
    feedback: str = ""
