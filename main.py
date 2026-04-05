import json
from fastapi import FastAPI, HTTPException
from Client import generate
from Prompt import analysis, generation
from os import environ as env
app = FastAPI()
language = env.get("language")

def safe_json_load(response_text):  
    try:
        return json.loads(response_text)
    except:
        return {
            "error": "Invalid LLM response",
            "raw": response_text
        }

@app.post("/analyze")
def analyze_req(data: dict):
    prompt = analysis(data["text"], language)
    result = generate(prompt)
    return safe_json_load(result)

@app.post("/generate")
def generate_req(data: dict):
    prompt = generation(data["description"], language)
    result = generate(prompt)
    return safe_json_load(result)