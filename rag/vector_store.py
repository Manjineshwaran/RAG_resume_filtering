import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def embed(self, text: str):
        return self.model.encode(text).tolist()

class VectorStore:
    def __init__(self, path="data/resumes.json"):
        self.embedder = Embedder()
        with open(path) as f:
            self.resumes = json.load(f)

        self.index = faiss.IndexFlatL2(384)  # 384 dims for MiniLM
        self.embeddings = []

        for r in self.resumes:
            emb = self.embedder.embed(r["text"])
            self.embeddings.append(emb)
            self.index.add(np.array([emb]).astype("float32"))

    def search(self, query: str, top_k=10):
        query_emb = self.embedder.embed(query)
        D, I = self.index.search(np.array([query_emb]).astype("float32"), top_k)
        return [self.resumes[i] for i in I[0]]
