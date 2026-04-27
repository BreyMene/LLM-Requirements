import faiss
import numpy as np
import pickle
import os

class VectorStore:
    def __init__(self, dim=384):
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []

    def add(self, embeddings, texts):
        self.index.add(np.array(embeddings).astype('float32'))
        self.texts.extend(texts)

    def search(self, query_embedding, k=3):
        D, I = self.index.search(query_embedding, k)
        return [self.texts[i] for i in I[0] if i < len(self.texts)]

    def save(self, path="vectorstore"):
        os.makedirs(path, exist_ok=True)
        faiss.write_index(self.index, f"{path}/index.faiss")
        with open(f"{path}/metadata.pkl", "wb") as f:
            pickle.dump(self.texts, f)

    def load(self, path="vectorstore"):
        try:
            self.index = faiss.read_index(f"{path}/index.faiss")
            with open(f"{path}/metadata.pkl", "rb") as f:
                self.texts = pickle.load(f)
        except:
            pass