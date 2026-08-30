from langchain_ollama import ChatOllama
from models import CodeStructure

llm = ChatOllama(model="qwen3:8b", temperature=0.2, reasoning=True)

structured_coder_llm = llm.with_structured_output(CodeStructure)
