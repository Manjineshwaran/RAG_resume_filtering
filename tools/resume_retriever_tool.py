# tools/resume_retriever_tool.py

from rag.vector_store import VectorStore

class ResumeRetrieverTool:
    def __init__(self):
        self.store = VectorStore()

    def run(self, input: dict):
        query_text = ", ".join(input.get("skills", [])) + f", {input.get('experience_years', 0)} years"
        return self.store.search(query_text, top_k=10)
