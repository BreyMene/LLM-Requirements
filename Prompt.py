def analysis_prompt(text):
    return f"""
Eres un analista de requisitos experto.

Analiza el siguiente requisito:
{text}

Responde:
1. Ambigüedades
2. Inconsistencias
3. Mejora sugerida
"""

def generation_prompt(description):
    return f"""
Eres un ingeniero de software.

A partir de esta descripción:
{description}

Genera:

1. Requisitos funcionales
2. Requisitos no funcionales

Sé claro y estructurado.
"""