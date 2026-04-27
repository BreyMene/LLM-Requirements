import faiss
import numpy as np
import pickle
import os

class VectorStore:
    def __init__(self, dim=384):
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []

    #Agregar nuevos textos
    def add(self, embeddings, texts):
        new_texts = []

        # Evitar duplicados
        for t in texts:
            if t not in self.texts:
                new_texts.append(t)

        if not new_texts:
            return

        import numpy as np
        embeddings = np.array(embeddings).astype('float32')

        self.index.add(embeddings[:len(new_texts)])
        self.texts.extend(new_texts)

    # Buscar los k textos más similares
    def search(self, query_embedding, k=3):
        D, I = self.index.search(query_embedding, k)
        return [self.texts[i] for i in I[0] if i < len(self.texts)]

    # Guardar el índice y los textos
    def save(self, path="vectorstore"):
        os.makedirs(path, exist_ok=True)
        faiss.write_index(self.index, f"{path}/index.faiss")
        with open(f"{path}/metadata.pkl", "wb") as f:
            pickle.dump(self.texts, f)

    # Cargar el índice y los textos
    def load(self, path="vectorstore"):
        try:
            self.index = faiss.read_index(f"{path}/index.faiss")
            with open(f"{path}/metadata.pkl", "rb") as f:
                self.texts = pickle.load(f)
        except:
            pass