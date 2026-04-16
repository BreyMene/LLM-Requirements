import requests
from os import environ as env

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate(prompt, model="mistral"):
    response = requests.post(OLLAMA_URL, json={
        "model": model,
        "prompt": prompt,
        "stream": False
    })
    
    data = response.json()
    if "response" in data:
        return data["response"]
    else:
        # Si hay error, devolver el mensaje de error
        return f"Error de Ollama: {data.get('error', 'Respuesta inesperada')}"