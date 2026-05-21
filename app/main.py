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

from datetime import datetime
import json
from pathlib import Path
from io import BytesIO

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from PyPDF2 import PdfReader

from app.services.rag import retrieve_context, index_documents
from app.services.llm import generate
from app.prompts.templates import analysis, generation

# Initialize FastAPI application
app = FastAPI()

# Resolve static directory relative to this file so the app works regardless
# of the working directory used to start the server.
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# Mount static files (HTML, CSS, JavaScript) at /assets endpoint
app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")

# Keep /static available for compatibility if needed
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def root():
    """
    Serve the main application page.
    
    Returns:
        FileResponse: The index.html file for the web interface.
    """
    return FileResponse(str(STATIC_DIR / "index.html"))


def allowed_file_extension(filename: str) -> bool:
    """Return whether the uploaded file type is allowed."""
    allowed_extensions = {".pdf", ".md", ".markdown", ".txt"}
    suffix = Path(filename).suffix.lower()
    return suffix in allowed_extensions


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes using PyPDF2."""
    reader = PdfReader(BytesIO(file_bytes))
    text = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text.append(page_text)
    return "\n".join(text).strip()


def chunk_text(text: str, size: int = 500, overlap: int = 150):
    """Split text into overlapping chunks for better retrieval."""
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if len(text) <= size:
        return [text]

    chunks = []
    step = max(size - overlap, 100)
    start = 0
    while start < len(text):
        chunk = text[start:start + size].strip()
        if chunk:
            chunks.append(chunk)
        start += step
    return chunks


def infer_document_type(filename: str) -> str:
    """Infer document type from the uploaded filename extension."""
    mapping = {
        ".pdf": "pdf",
        ".md": "markdown",
        ".markdown": "markdown",
        ".txt": "text"
    }
    return mapping.get(Path(filename).suffix.lower(), "text")


def build_metadata(date_created: str, document_type: str, summary: str, notes: str):
    """Create a consistent JSON metadata object for each document chunk."""
    return {
        "date_created": date_created or datetime.utcnow().isoformat(),
        "document_type": document_type or "text",
        "summary": summary or "User-provided document",
        "notes": notes or "No additional notes provided"
    }


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

    prepared_items = []
    for item in docs:
        # Accept either raw string text or structured document objects
        if isinstance(item, dict):
            content = item.get("content", "").strip()
            if len(content) <= 5:
                continue
            metadata = build_metadata(
                item.get("date_created", ""),
                item.get("document_type", ""),
                item.get("summary", ""),
                item.get("notes", "")
            )
        else:
            content = str(item).strip()
            if len(content) <= 5:
                continue
            metadata = build_metadata("", "text", "User-provided text", "Added via UI")

        chunked_texts = chunk_text(content)
        for idx, chunk in enumerate(chunked_texts):
            prepared_items.append({
                "content": chunk,
                "metadata": {
                    **metadata,
                    "chunk_index": idx + 1,
                    "original_length": len(content)
                }
            })

    if not prepared_items:
        raise HTTPException(status_code=400, detail="No valid docs after processing")

    index_documents(prepared_items)

    return {
        "status": "ok",
        "original_docs": len(docs),
        "processed_docs": len(prepared_items)
    }


@app.post("/train-file")
async def train_file(
    file: UploadFile = File(...),
    date_created: str = Form(None),
    document_type: str = Form(None),
    summary: str = Form(None),
    notes: str = Form(None),
):
    """
    Upload a PDF or markdown document and index its text with metadata.
    """
    if not allowed_file_extension(file.filename):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    content_bytes = await file.read()
    extension = Path(file.filename).suffix.lower()

    if extension == ".pdf":
        text = extract_text_from_pdf(content_bytes)
    else:
        text = content_bytes.decode("utf-8", errors="ignore")

    if not text or len(text.strip()) <= 5:
        raise HTTPException(status_code=400, detail="No valid text extracted from the uploaded file")

    detected_type = infer_document_type(file.filename)
    metadata = build_metadata(date_created, detected_type, summary, notes)
    chunks = chunk_text(text)
    prepared_items = [
        {
            "content": chunk,
            "metadata": {
                **metadata,
                "source_file": file.filename,
                "chunk_index": idx + 1,
                "original_type": detected_type
            }
        }
        for idx, chunk in enumerate(chunks)
    ]

    index_documents(prepared_items)
    return {
        "status": "ok",
        "source_file": file.filename,
        "chunks_indexed": len(prepared_items),
        "metadata": metadata
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