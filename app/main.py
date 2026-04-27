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
    
    index_documents(docs)
    return {"status": "ok", "docs_indexed": len(docs)}

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