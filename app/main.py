from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.services.rag import retrieve_context, index_documents
from app.services.llm import generate
from app.prompts.templates import analysis, generation

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")

# ENTRENAR RAG
@app.post("/train")
def train(data: dict):
    docs = data.get("docs", [])

    if not docs:
        raise HTTPException(status_code=400, detail="No docs provided")

    # Limpieza
    clean_docs = []
    for d in docs:
        if isinstance(d, str):
            d = d.strip()
            if len(d) > 5:
                clean_docs.append(d)

    if not clean_docs:
        raise HTTPException(status_code=400, detail="No valid docs")

    # Chunking
    def chunk_text(text, size=200):
        return [text[i:i+size] for i in range(0, len(text), size)]

    final_docs = []
    for doc in clean_docs:
        chunks = chunk_text(doc)
        final_docs.extend(chunks)

    # Indexar
    index_documents(final_docs)

    return {
        "status": "ok",
        "original_docs": len(docs),
        "processed_docs": len(final_docs)
    }

# ANALIZAR
@app.post("/analyze")
def analyze_req(data: dict):
    text = data.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Text required")

    context = retrieve_context(text)
    prompt = analysis(text, context)

    result = generate(prompt)
    return {"analysis": result}

# GENERAR
@app.post("/generate")
def generate_req(data: dict):
    description = data.get("description", "")
    if not description:
        raise HTTPException(status_code=400, detail="Description required")

    context = retrieve_context(description)
    prompt = generation(description, context)

    result = generate(prompt)
    return {"requirements": result}