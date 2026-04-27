# LLM Requirements Auditor

An intelligent, AI-powered web application for analyzing and generating software requirements following IEEE 830 and Gherkin (BDD) standards. Built with FastAPI, FAISS vector search, and a local Ollama LLM backend.

## Overview

This application helps software engineers and requirements analysts:
- **Audit requirements** for clarity, completeness, and standards compliance
- **Generate structured requirements** from natural language descriptions
- **Build a knowledge base** of reference requirements for context-aware suggestions
- **Follow best practices** with IEEE 830 and Gherkin Given-When-Then formats

### Key Features

✅ **Standards-Based Analysis**
- IEEE 830 compliance checks (Functional/Non-Functional classification)
- Gherkin (BDD) syntax for testable requirements
- Measurable acceptance criteria validation

✅ **RAG-Enhanced Generation**
- Semantic similarity search using FAISS vector database
- Context-aware suggestions from reference documents
- Relevant examples automatically retrieved

✅ **AI-Powered Insights**
- Local LLM integration (Ollama/Mistral)
- No cloud dependencies - fully private
- Extensible to other models

✅ **User-Friendly Interface**
- Modern, responsive web UI
- Three tabs: Analyze, Generate, Add Documents
- Real-time feedback with loading indicators

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │ API Endpoints                                   │    │
│  ├─────────────────────────────────────────────────┤    │
│  │ POST /analyze      - Audit a requirement        │    │
│  │ POST /generate     - Create requirements        │    │
│  │ POST /train        - Add documents to KB        │    │
│  │ GET  /             - Serve web interface        │    │
│  └─────────────────────────────────────────────────┘    │
│                           ↕                             │
│  ┌─────────────────────────────────────────────────┐    │
│  │ RAG Pipeline (app/services/rag.py)              │    │
│  ├─────────────────────────────────────────────────┤    │
│  │ • retrieve_context() - Semantic search          │    │
│  │ • index_documents() - Add to knowledge base     │    │
│  └─────────────────────────────────────────────────┘    │
│            ↕                          ↕                 │
│  ┌────────────────────────┐  ┌──────────────────────┐   │
│  │ FAISS Vector Store     │  │ Ollama LLM Service   │   │
│  │ (app/db)               │  │ (app/services/llm.py)│   │
│  │ • Embeddings stored    │  │ • Model: Mistral     │   │
│  │ • Semantic search      │  │ • localhost:11434    │   │ 
│  │ • Persistence (disk)   │  │ • Non-streaming      │   │
│  └────────────────────────┘  └──────────────────────┘   │
│            ↕                                            │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Embeddings Service (app/services/embeddings.py)    │ │
│  ├────────────────────────────────────────────────────┤ │
│  │ • Model: all-MiniLM-L6-v2 (384-dim)                │ │
│  │ • Text → Vector conversion                         │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│        Web Frontend (static/index.html)                 │
├─────────────────────────────────────────────────────────┤
│ • HTML/CSS/JavaScript                                   │
│ • Responsive tab-based UI                               │
│ • Real-time loading/error states                        │
└─────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
LLM-Requirements/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry point
│   ├── db/
│   │   └── vector_store.py         # FAISS vector database wrapper
│   ├── services/
│   │   ├── rag.py                  # RAG pipeline implementation
│   │   ├── llm.py                  # LLM service (Ollama integration)
│   │   └── embeddings.py           # Text embedding service
│   └── prompts/
│       └── templates.py             # Prompt templates (analysis & generation)
├── static/
│   └── index.html                   # Web interface
├── vectorstore/
│   ├── index.faiss                 # FAISS index (persisted)
│   └── metadata.pkl                # Document metadata
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
└── LICENSE
```

---

## Setup & Installation

### Prerequisites

1. **Python 3.8+**
2. **Ollama** installed and running locally
   - Download: https://ollama.ai
   - Run: `ollama serve` (default: localhost:11434)
   - Pull model: `ollama pull mistral` (or your preferred model)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LLM-Requirements
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate          # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Ollama is running**
   ```bash
   curl http://localhost:11434/api/tags
   # Should return available models
   ```

5. **Start the application**
   ```bash
   uvicorn app.main:app --reload
   ```
   - Application runs at: http://localhost:8000
   - API docs: http://localhost:8000/docs (Swagger UI)

---

## Dependencies

| Package | Purpose |
|---------|---------|
| **fastapi** | Web framework for API endpoints |
| **uvicorn** | ASGI web server |
| **faiss-cpu** | Vector similarity search database |
| **sentence-transformers** | Text embedding model (all-MiniLM-L6-v2) |
| **requests** | HTTP client for Ollama API |
| **numpy** | Numerical computing (FAISS dependency) |

Install all: `pip install -r requirements.txt`

---

## API Endpoints

### 1. **GET /** - Serve Web Interface
Returns the main web application (index.html).

```bash
curl http://localhost:8000/
```

---

### 2. **POST /analyze** - Audit a Requirement

Analyzes a requirement statement for quality, clarity, and standards compliance.

**Request:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The system must process user requests quickly and securely"
  }'
```

**Response:**
```json
{
  "analysis": "CLASSIFICATION:\n- Tipo: Non-Functional (RNF)\n- Categoría: Performance, Security\n\nCLARIDAD Y CALIDAD:\n- ¿Es claro y medible?: No\n- Problemas encontrados:\n  • 'quickly' is not measurable\n  • 'securely' needs specific security standards\n\nMÉTRICA GHERKIN:\n- Dado: System is ready to process requests\n- Cuando: User submits request\n- Entonces: Response received in <100ms with encryption\n\nRECOMENDACIÓN:\n[RF-001] User Request Processing\nDescription: System shall process user requests within 100ms using TLS 1.2 encryption..."
}
```

**Analysis Includes:**
- Classification (Functional/Non-Functional)
- Quality assessment and issues found
- Gherkin Given-When-Then format
- Specific recommendations for improvement

---

### 3. **POST /generate** - Generate Requirements

Creates comprehensive requirements (both functional and non-functional) from a description.

**Request:**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "An authentication system using OAuth 2.0 with two-factor authentication"
  }'
```

**Response:**
```json
{
  "requirements": "====== REQUISITOS FUNCIONALES ======\n\n[RF-001] User Login with OAuth 2.0\nPrioridad: Alta\nDescripción: Users shall authenticate using OAuth 2.0 providers (Google, GitHub, Microsoft)...\n\nMétrica Gherkin:\n  Dado: User is on the login page\n  Cuando: User clicks 'Login with Google'\n  Entonces: User is redirected to Google OAuth consent screen and authenticated\n\nCriterios de aceptación:\n  • OAuth provider is accessible\n  • Token refresh happens automatically\n  • User data is securely stored\n\n[RF-002] Two-Factor Authentication\n...\n\n====== REQUISITOS NO-FUNCIONALES ======\n\n[RNF-001] Authentication Response Time\nCategoría: Performance\nPrioridad: Alta\n\nEspecificación cuantificable:\n  - Métrica: End-to-end authentication time\n  - Umbral: < 2 seconds\n  - Unidad: ms\n..."
}
```

**Generation Includes:**
- Functional Requirements (RF-###) with descriptions
- Non-Functional Requirements (RNF-###) with metrics
- Gherkin Given-When-Then acceptance criteria
- Priority levels and stakeholder information
- Service Level Agreements (SLA) when applicable

---

### 4. **POST /train** - Add Documents to Knowledge Base

Indexes new documents to enhance context-aware suggestions.

**Request:**
```bash
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d '{
    "docs": [
      "Authentication requirements must follow OAuth 2.0 specification",
      "Performance: API endpoints must respond within 100ms for 95th percentile latency",
      "Security: All data in transit must use TLS 1.2 or higher"
    ]
  }'
```

**Response:**
```json
{
  "status": "ok",
  "original_docs": 3,
  "processed_docs": 5
}
```

**Processing Details:**
- **Cleaning:** Removes whitespace, filters texts < 6 characters
- **Chunking:** Splits long documents into 200-character segments
- **Embedding:** Converts chunks to semantic vectors (384-dimensional)
- **Indexing:** Stores in FAISS for semantic search
- **Persistence:** Automatically saves to `vectorstore/` directory

---

## Usage Examples

### Example 1: Analyze a Poorly-Written Requirement

```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={"text": "The system must be good"}
)

analysis = response.json()["analysis"]
print(analysis)
# Output: Identifies that "good" is unmeasurable, suggests specific criteria...
```

### Example 2: Build a Knowledge Base, Then Generate Requirements

```python
import requests

# Step 1: Add reference requirements
requests.post(
    "http://localhost:8000/train",
    json={
        "docs": [
            "Authentication shall support OAuth 2.0, SAML, and LDAP providers",
            "API response time must be < 200ms for 99th percentile",
            "Data must be encrypted at rest using AES-256"
        ]
    }
)

# Step 2: Generate requirements with context
response = requests.post(
    "http://localhost:8000/generate",
    json={"description": "Build a user management system"}
)

requirements = response.json()["requirements"]
print(requirements)
# Output: Includes reference to OAuth 2.0, performance SLAs, encryption standards...
```

### Example 3: Complete Workflow with Web UI

1. Open http://localhost:8000/
2. Go to **"➕ Add Text"** tab
3. Paste your reference requirements:
   ```
   Users must be able to create accounts with email and password.
   Account verification is required via email link (24-hour expiration).
   Passwords must meet NIST SP 800-63B requirements.
   ```
4. Click **"Agregar Texto"** to add to knowledge base
5. Go to **"✨ Generate"** tab
6. Enter: `"Build a secure user registration system"`
7. Click **"Generate"** - receives tailored requirements informed by your reference docs

---

## Configuration

### LLM Model Selection

Edit `app/services/llm.py` to change the model:

```python
# Default: Mistral
def generate(prompt, model="mistral"):
    # ...

# Or use: "neural-chat", "llama2", "openhermes", etc.
def generate(prompt, model="neural-chat"):
    # ...
```

**Available models** (requires `ollama pull <model>`):
- `mistral` - Fast, good for most tasks (default)
- `neural-chat` - Optimized for conversational tasks
- `llama2` - Larger model with better context understanding
- `openhermes` - OpenHermes model variant

### Embedding Model

The embedding model is fixed to `all-MiniLM-L6-v2` (384 dimensions) in `app/services/embeddings.py`.

To change:
```python
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')  # 768 dims
# Also update VectorStore(dim=768) in vector_store.py
```

### Vector Store Persistence

Vector store is automatically saved to `vectorstore/` directory:
- `index.faiss` - FAISS binary index
- `metadata.pkl` - Document metadata

Clear the knowledge base:
```bash
rm -rf vectorstore/
# Or on Windows:
rmdir /s vectorstore
```

---

## Troubleshooting

### Issue: "Connection refused" when calling LLM

**Solution:** Ensure Ollama is running:
```bash
ollama serve
# In another terminal:
ollama pull mistral
```

### Issue: FAISS index errors

**Solution:** Delete and rebuild the vector store:
```bash
rm -rf vectorstore/
# Restart the application - index will be recreated
```

### Issue: Out of memory with large documents

**Solution:** The `/train` endpoint automatically chunks documents (200 chars each). If still memory-intensive:
- Process smaller batches
- Clear the vector store periodically
- Consider FAISS GPU variant for large-scale deployments

### Issue: Slow semantic search

**Possible causes:**
- Large number of documents in index
- FAISS CPU performance limitations
- **Solution:** Use `faiss-gpu` or reduce document count

---

## Performance Considerations

| Operation | Time | Notes |
|-----------|------|-------|
| Embedding text | 100-500ms | Depends on text length, first request loads model |
| FAISS search (1000 docs) | 10-50ms | Very fast, O(n) linear scan |
| LLM generation | 5-60s | Depends on prompt length, model size, hardware |
| Full request (/analyze) | 10-70s | Embedding + search + LLM generation |

**Optimization Tips:**
- Cache embeddings for repeated queries
- Use `faiss-gpu` for production deployments
- Monitor Ollama memory usage
- Consider quantized models for resource-constrained environments

---

## Standards & References

### IEEE 830 - Software Requirements Specification
- **Functional Requirements (RF):** What the system shall do
- **Non-Functional Requirements (RNF):** How well the system shall do it
  - Categories: Performance, Security, Usability, Reliability, Availability, Maintainability

**Application:** Analysis and generation prompts follow IEEE 830 structure for requirement classification and quality assessment.

### Gherkin (BDD) - Given-When-Then Format
```gherkin
Given [initial state/precondition]
When  [action/event]
Then  [observable result]
```

**Application:** All generated requirements include Gherkin syntax for testable acceptance criteria, enabling automated testing and requirement validation.

### SMART Criteria for Requirements
- **Specific:** Clear, detailed, unambiguous
- **Measurable:** Quantifiable with metrics
- **Achievable:** Realistic and feasible
- **Relevant:** Aligned with goals
- **Time-bound:** Has deadline (when applicable)

---

## Development & Contribution

### Code Structure

- `app/main.py` - API endpoints and request handling
- `app/services/` - Business logic (RAG, LLM, embeddings)
- `app/db/` - Data persistence layer
- `app/prompts/` - Prompt engineering templates
- `static/` - Frontend (JavaScript, HTML)

### Adding New Features

1. **New LLM prompt template:** Add function to `app/prompts/templates.py`
2. **New API endpoint:** Add function to `app/main.py`
3. **New embedding model:** Modify `app/services/embeddings.py`
4. **Frontend changes:** Edit `static/index.html`

---

## License

[See LICENSE file](LICENSE)

---

## Support & Questions

For issues, questions, or suggestions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the API documentation at http://localhost:8000/docs
3. Check Ollama logs: `ollama serve` output
4. Verify dependencies: `pip list | grep -E "fastapi|faiss|sentence-transformers"`

---

**Built with ❤️ using FastAPI, FAISS, and Ollama**