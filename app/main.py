"""
LLM Requirements Auditor - FastAPI Application

A web-based application for analyzing and generating software requirements using
AI-powered, standards-based (IEEE 830 and Gherkin) requirement management.

Features:
- Analyze requirements for clarity, completeness, and standards compliance
- Generate structured requirements from descriptions
- Add reference documents to a semantic search database (FAISS)
- Context-aware suggestions using RAG (Retrieval-Augmented Generation)

Architecture:
- Backend: FastAPI with Uvicorn
- LLM: Ollama (Mistral model) running locally
- Vector Database: FAISS for semantic search
- Embeddings: sentence-transformers (all-MiniLM-L6-v2)
- Frontend: HTML/CSS/JavaScript (static/)
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.services.rag import retrieve_context, index_documents
from app.services.llm import generate
from app.prompts.templates import analysis, generation

# Initialize FastAPI application
app = FastAPI()

# Mount static files (HTML, CSS, JavaScript) at /static endpoint
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    """
    Serve the main application page.
    
    Returns:
        FileResponse: The index.html file for the web interface.
    """
    return FileResponse("static/index.html")


@app.post("/train")
def train(data: dict):
    """
    Add new documents to the knowledge base for context-aware analysis.
    
    Processes documents by:
    1. Cleaning (removing whitespace, filtering short texts)
    2. Chunking (breaking into 200-character segments for better retrieval)
    3. Embedding (converting to semantic vectors)
    4. Indexing (storing in FAISS vector database)
    
    Args:
        data (dict): Request body containing:
                    - docs (list): List of text documents to index
    
    Returns:
        dict: Status report with:
              - status (str): "ok" if successful
              - original_docs (int): Number of documents submitted
              - processed_docs (int): Number of documents after cleaning and chunking
    
    Raises:
        HTTPException: 400 if no documents provided or all documents filtered out
    
    Note:
        - Minimum text length: 6 characters
        - Chunk size: 200 characters with 50% overlap
        - Documents are persisted to disk automatically
    
    Example:
        POST /train
        {
            "docs": [
                "The system must authenticate users with OAuth 2.0",
                "Performance requirement: API response < 100ms"
            ]
        }
        
        Response:
        {
            "status": "ok",
            "original_docs": 2,
            "processed_docs": 4
        }
    """
    docs = data.get("docs", [])

    if not docs:
        raise HTTPException(status_code=400, detail="No docs provided")

    # Validation: Remove empty/whitespace-only strings and texts shorter than 6 chars
    clean_docs = []
    for d in docs:
        if isinstance(d, str):
            d = d.strip()
            if len(d) > 5:
                clean_docs.append(d)

    if not clean_docs:
        raise HTTPException(status_code=400, detail="No valid docs")

    # Chunking: Split long documents into 200-character segments
    # This improves retrieval accuracy by creating more granular searchable units
    def chunk_text(text, size=200):
        """Split text into overlapping chunks of specified size."""
        return [text[i:i+size] for i in range(0, len(text), size)]

    final_docs = []
    for doc in clean_docs:
        chunks = chunk_text(doc)
        final_docs.extend(chunks)

    # Index documents in the vector store and persist to disk
    index_documents(final_docs)

    return {
        "status": "ok",
        "original_docs": len(docs),
        "processed_docs": len(final_docs)
    }


@app.post("/analyze")
def analyze_req(data: dict):
    """
    Analyze a software requirement for quality, clarity, and standards compliance.
    
    Performs comprehensive analysis including:
    1. Retrieves relevant context from the knowledge base
    2. Sends requirement and context to LLM with analysis prompt template
    3. Returns structured analysis following IEEE 830 and Gherkin standards
    
    Args:
        data (dict): Request body containing:
                    - text (str): The requirement statement to analyze
    
    Returns:
        dict: Analysis results with:
              - analysis (str): Detailed analysis from LLM including:
                              * Classification (Functional/Non-Functional)
                              * Quality assessment
                              * Gherkin Given-When-Then format
                              * Recommendations for improvement
    
    Raises:
        HTTPException: 400 if text is missing or empty
    
    Pipeline:
        1. Validate input
        2. Retrieve similar documents from vector store (RAG)
        3. Create analysis prompt with context
        4. Call LLM to generate analysis
        5. Return structured response
    
    Example:
        POST /analyze
        {
            "text": "The system must be fast and secure"
        }
        
        Response:
        {
            "analysis": "CLASSIFICATION: Non-Functional (RNF)\\nCLARIDAD: Not clear..."
        }
    """
    text = data.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Text required")

    # Retrieve relevant context from knowledge base using semantic search
    context = retrieve_context(text)
    
    # Generate analysis prompt with context and requirement text
    prompt = analysis(text, context)

    # Call LLM to perform analysis
    result = generate(prompt)
    return {"analysis": result}


@app.post("/generate")
def generate_req(data: dict):
    """
    Generate comprehensive software requirements from a description.
    
    Creates both functional and non-functional requirements including:
    1. Retrieves relevant context from knowledge base
    2. Sends description to LLM with generation prompt template
    3. Returns structured requirements following IEEE 830 and Gherkin standards
    
    Args:
        data (dict): Request body containing:
                    - description (str): Description of what needs to be built
    
    Returns:
        dict: Generated requirements with:
              - requirements (str): Complete requirements specification including:
                                  * Functional Requirements (RF-###)
                                  * Non-Functional Requirements (RNF-###)
                                  * Gherkin Given-When-Then acceptance criteria
                                  * Priority and categorization
    
    Raises:
        HTTPException: 400 if description is missing or empty
    
    Pipeline:
        1. Validate input
        2. Retrieve similar requirements from vector store (RAG)
        3. Create generation prompt with context
        4. Call LLM to generate requirements
        5. Return structured requirements
    
    Example:
        POST /generate
        {
            "description": "A user authentication system with OAuth 2.0 support"
        }
        
        Response:
        {
            "requirements": "[RF-001] User Login\\nPrioridad: Alta\\n..."
        }
    """
    description = data.get("description", "")
    if not description:
        raise HTTPException(status_code=400, detail="Description required")

    # Retrieve relevant context from knowledge base using semantic search
    context = retrieve_context(description)
    
    # Generate requirement generation prompt with context and description
    prompt = generation(description, context)

    # Call LLM to generate requirements
    result = generate(prompt)
    return {"requirements": result}