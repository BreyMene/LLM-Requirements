from fastapi import FastAPI
from Client import generate
from Prompt import analysis_prompt, generation_prompt

app = FastAPI()

@app.get("/")
def root():
    return {"message": "LLM Requisitos API"}

@app.post("/analyze")
def analyze_req(data: dict):
    prompt = analysis_prompt(data["text"])
    result = generate(prompt)
    return {"result": result}

@app.post("/generate")
def generate_req(data: dict):
    prompt = generation_prompt(data["description"])
    result = generate(prompt)
    return {"result": result}