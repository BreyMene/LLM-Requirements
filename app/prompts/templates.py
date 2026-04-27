def analysis(text, context, language="es"):
    return f"""
Eres un auditor experto en requisitos siguiendo estándares IEEE 830 y Gherkin.

Contexto relevante:
{context}

Analiza el siguiente requisito:
"{text}"

Responde en formato de lista estructurada siguiendo IEEE 830:

1. CLASIFICACIÓN:
   - Tipo: [Funcional (RF) o No-Funcional (RNF)]
   - Categoría (si es RNF): Performance, Seguridad, Usabilidad, Confiabilidad, Disponibilidad, etc.

2. CLARIDAD Y CALIDAD:
   - ¿Es claro y medible?: [Sí/No]
   - Problemas encontrados: [lista de problemas]

3. MÉTRICA GHERKIN:
   - Dado (Given): [condición inicial]
   - Cuando (When): [acción]
   - Entonces (Then): [resultado esperado]

4. RECOMENDACIÓN:
   - Mejora sugerida: [cómo optimizarlo]
   - Requisito reformulado con criterios de aceptación medibles
"""

def generation(description, context, language="es"):
    return f"""
Eres un experto en ingeniería de requisitos con dominio de IEEE 830 y Gherkin.

Contexto relevante:
{context}

Genera requisitos para:
"{description}"

Responde como lista estructurada siguiendo IEEE 830 con métricas Gherkin:

====== REQUISITOS FUNCIONALES ======

[RF-###] TÍTULO
Prioridad: [Alta/Media/Baja]
Descripción: [explicación clara del qué y para qué]

Métrica Gherkin:
  Dado (Given): [estado inicial/precondición]
  Cuando (When): [acción del usuario/sistema]
  Entonces (Then): [resultado observable y verificable]

Criterios de aceptación:
  • [criterio medible 1]
  • [criterio medible 2]
  • [criterio medible 3]

Fuente/Stakeholder: [quién solicitó]
Estado: [Nuevo/Validado/Aprobado]

---

====== REQUISITOS NO-FUNCIONALES ======

[RNF-###] TÍTULO
Categoría: [Performance/Seguridad/Usabilidad/Confiabilidad/Disponibilidad/Mantenibilidad]
Prioridad: [Alta/Media/Baja]

Especificación cuantificable:
  - Métrica: [qué se mide]
  - Umbral: [valor o rango aceptable]
  - Unidad: [ms, %, usuario, etc.]

Métrica Gherkin:
  Dado (Given): [condición de prueba]
  Cuando (When): [escenario de carga/situación]
  Entonces (Then): [límite o métrica debe cumplirse]

Acuerdo de nivel de servicio (SLA): [si aplica]

Repite este patrón para cada requisito identificado.
"""