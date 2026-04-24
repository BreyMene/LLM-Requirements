def analysis(text, language="es"):
    lang_instruction = "en inglés" if language == "en" else "en español"
    return f"""Eres un auditor de requisitos. Analiza este requisito y responde SOLO en JSON válido, sin texto adicional:

"{text}"

Responde {lang_instruction} en este formato JSON exacto:
{{
  "classification": "Funcional o No-Funcional",
  "is_clear": true,
  "issues": ["lista de problemas encontrados"],
  "suggestion": "cómo mejorarlo"
}}"""


def generation(description, language="es"):
    lang_instruction = "en inglés" if language == "en" else "en español"
    return f"""Eres un experto en requisitos. Genera requisitos para esta descripción y responde SOLO en JSON válido, sin texto adicional:

"{description}"

Responde {lang_instruction} exactamente en este formato:
{{
  "requirements": [
    {{
      "id": "RF-001",
      "title": "nombre",
      "description": "descripción clara",
      "type": "funcional"
    }}
  ]
}}"""