"""
Prompt Templates for Requirements Analysis and Generation

This module contains specialized prompt templates following IEEE 830 standard
and Gherkin (BDD) syntax. These templates are used to instruct the LLM on how to
analyze and generate software requirements with consistent, measurable criteria.

Standards:
- IEEE 830: Standard for Software Requirements Specifications
- Gherkin: Behavior-Driven Development syntax (Given-When-Then)
"""


def analysis(text, context, language="es"):
    """
    Generate a prompt for analyzing and auditing software requirements.
    
    Creates a structured prompt that instructs the LLM to analyze a requirement
    against IEEE 830 and Gherkin standards, identifying issues and suggesting improvements.
    
    Args:
        text (str): The requirement statement to analyze.
                   Example: "The system must be fast and secure"
        context (str): Relevant context retrieved from the RAG vector store.
                      Contains similar requirements or standards for comparison.
        language (str, optional): Language for the response. Defaults to "es" (Spanish).
    
    Returns:
        str: A formatted prompt ready to send to the LLM.
    
    Output Sections (included in prompt):
        1. CLASSIFICATION: Identifies if requirement is Functional (RF) or Non-Functional (RNF)
        2. CLARITY AND QUALITY: Evaluates how well-defined the requirement is
        3. GHERKIN METRIC: Converts requirement to Given-When-Then format
        4. RECOMMENDATION: Suggests improvements and reformulates the requirement
    
    Example:
        >>> prompt = analysis("The system must handle 1000 users", "context...")
        >>> # Prompt instructs LLM to classify, evaluate, and improve the requirement
    """
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
    """
    Generate a prompt for creating comprehensive software requirements.
    
    Creates a structured prompt that instructs the LLM to generate both functional
    and non-functional requirements based on a description, following IEEE 830 and
    Gherkin standards with measurable acceptance criteria.
    
    Args:
        description (str): Description of what needs to be built.
                          Example: "A user authentication system with two-factor authentication"
        context (str): Relevant context from the RAG vector store.
                      Contains similar requirements or best practices.
        language (str, optional): Language for the response. Defaults to "es" (Spanish).
    
    Returns:
        str: A formatted prompt ready to send to the LLM.
    
    Output Structure (included in prompt):
        - FUNCTIONAL REQUIREMENTS (RF):
          * ID, Title, Priority
          * Description
          * Gherkin Given-When-Then format
          * Acceptance criteria (measurable)
        
        - NON-FUNCTIONAL REQUIREMENTS (RNF):
          * ID, Category (Performance, Security, Usability, etc.)
          * Priority
          * Quantifiable specification with metrics
          * SLA (Service Level Agreement) if applicable
    
    Example:
        >>> prompt = generation("A payment system", "context...")
        >>> # Prompt instructs LLM to generate detailed, structured requirements
    """
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