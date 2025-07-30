from google.generativeai import embed

class Embedder:
    def __init__(self):
        self.model = embed.GoogleEmbeddings("models/embedding-001")

    def embed(self, text: str):
        return self.model.embed_query(text)
