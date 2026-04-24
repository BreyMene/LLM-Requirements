import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from Client import generate
from Prompt import analysis, generation
from os import environ as env
from pathlib import Path
import requests
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Servir archivos estáticos
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Configurar idioma (por defecto 'es' para español)
language = env.get("language", "es")
USE_MOCK = env.get("USE_MOCK", "false").lower() == "true"

def safe_json_load(response_text):  
    try:
        return json.loads(response_text)
    except:
        return {
            "error": "Invalid LLM response",
            "raw": response_text
        }

def get_mock_response(request_type: str, text: str):
    """Genera respuestas simuladas para demostración"""
    if request_type == "analyze":
        return {
            "classification": "Funcional",
            "is_clear": True,
            "issues": ["Podría ser más específico"],
            "suggestion": "Agregar métricas de rendimiento específicas"
        }
    else:  # generate
        return {
            "requirements": [
                {
                    "id": "RF-001",
                    "title": "Autenticación de Usuario",
                    "description": "El sistema debe autenticar usuarios de forma segura",
                    "type": "funcional"
                },
                {
                    "id": "RF-002",
                    "title": "Autorización",
                    "description": "El sistema debe verificar permisos de usuario",
                    "type": "funcional"
                }
            ]
        }

@app.get("/health")
def health_check():
    """Verifica que Ollama está disponible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            if not models.get('models'):
                return {
                    "status": "WARNING",
                    "ollama": "Sin modelos instalados",
                    "models": [],
                    "message": "Ollama está corriendo pero no hay modelos. Ejecuta: ollama pull mistral"
                }
            return {"status": "OK", "ollama": response.json()}
        else:
            raise HTTPException(status_code=503, detail="Ollama no respondió correctamente")
    except requests.exceptions.ConnectionError:
        if USE_MOCK:
            return {"status": "MOCK", "message": "Usando modo simulado (Ollama no disponible)"}
        raise HTTPException(status_code=503, detail="Ollama no está disponible en http://localhost:11434")

@app.post("/analyze")
def analyze_req(data: dict):
    try:
        if USE_MOCK:
            logger.info("MODO SIMULADO: Analizando requisito")
            return get_mock_response("analyze", data.get("text", ""))
            
        logger.info(f"Analizando: {data.get('text', '')[:100]}...")
        
        # Validar entrada
        if "text" not in data or not data["text"].strip():
            raise ValueError("El campo 'text' es requerido y no puede estar vacío")
        
        # Generar prompt
        prompt = analysis(data["text"], language)
        logger.info(f"Prompt generado, enviando a Ollama...")
        
        # Llamar a Ollama
        result = generate(prompt)
        logger.info(f"Respuesta de Ollama recibida")
        
        # Parsear JSON
        parsed = safe_json_load(result)
        logger.info(f"Análisis completado exitosamente")
        return parsed
        
    except ValueError as ve:
        logger.error(f"Validación error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Conexión a Ollama rechazada")
        if USE_MOCK:
            logger.info("Usando respuesta simulada")
            return get_mock_response("analyze", data.get("text", ""))
        raise HTTPException(
            status_code=503,
            detail="Ollama no está disponible. Configura USE_MOCK=true para simular respuestas"
        )
    except Exception as e:
        logger.error(f"Error en analyze_req: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/generate")
def generate_req(data: dict):
    try:
        if USE_MOCK:
            logger.info("MODO SIMULADO: Generando requisitos")
            return get_mock_response("generate", data.get("description", ""))
            
        logger.info(f"Generando: {data.get('description', '')[:100]}...")
        
        # Validar entrada
        if "description" not in data or not data["description"].strip():
            raise ValueError("El campo 'description' es requerido y no puede estar vacío")
        
        # Generar prompt
        prompt = generation(data["description"], language)
        logger.info(f"Prompt generado, enviando a Ollama...")
        
        # Llamar a Ollama
        result = generate(prompt)
        logger.info(f"Respuesta de Ollama recibida")
        
        # Parsear JSON
        parsed = safe_json_load(result)
        logger.info(f"Generación completada exitosamente")
        return parsed
        
    except ValueError as ve:
        logger.error(f"Validación error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Conexión a Ollama rechazada")
        if USE_MOCK:
            logger.info("Usando respuesta simulada")
            return get_mock_response("generate", data.get("description", ""))
        raise HTTPException(
            status_code=503,
            detail="Ollama no está disponible. Configura USE_MOCK=true para simular respuestas"
        )
    except Exception as e:
        logger.error(f"Error en generate_req: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.get("/")
def root():
    return FileResponse(static_dir / "index.html")