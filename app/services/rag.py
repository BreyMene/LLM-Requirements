from app.services.embeddings import embed
from app.db.vector_store import VectorStore

vector_store = VectorStore()

# Cargar índice si existe
vector_store.load()

def index_documents(docs):
    embeddings = embed(docs)
    vector_store.add(embeddings, docs)
    vector_store.save()

def retrieve_context(query):
    if len(vector_store.texts) == 0:
        return "No hay contexto disponible."
    
    query_embedding = embed([query])
    results = vector_store.search(query_embedding, k=3)
    return "\n".join(results)