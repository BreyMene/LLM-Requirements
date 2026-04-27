from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed(texts):
    return model.encode(texts, show_progress_bar=False)