"""
Retrieval-Augmented Generation (RAG) Service

This module implements the core RAG pipeline for the requirements auditor application.
It handles:
1. Document indexing: Adding new documents to the vector store
2. Context retrieval: Finding relevant documents for a given query

The RAG pattern enhances LLM responses with relevant context from stored documents,
improving the quality and accuracy of requirement analysis and generation.
"""

from app.services.embeddings import embed
from app.db.vector_store import VectorStore

# Initialize the vector store and load any previously saved index
vector_store = VectorStore()
vector_store.load()


def index_documents(docs):
    """
    Index new documents into the vector store for semantic search.
    
    This function:
    1. Converts documents to embeddings using the sentence transformer
    2. Adds embeddings and texts to the vector store (deduplicates automatically)
    3. Persists the updated index to disk
    
    Args:
        docs (list): List of text documents to index.
                    Documents should be meaningful text chunks (typically 100-500 tokens).
    
    Returns:
        None: Modifies the vector store in-place and saves it to disk.
    
    Note:
        - Duplicate documents are automatically filtered out by VectorStore.add()
        - The operation is persistent - saved documents remain available after restart
    
    Example:
        >>> index_documents(["API requirements for authentication", "Database schema design"])
    """
    embeddings = embed(docs)
    vector_store.add(embeddings, docs)
    vector_store.save()


def retrieve_context(query):
    """
    Retrieve relevant context documents for a given query using semantic similarity.
    
    Performs semantic search in the vector store to find documents most similar
    to the input query. Results are ranked by relevance (most similar first).
    
    Args:
        query (str): The search query or text requiring context.
                    Example: "authentication system for users"
    
    Returns:
        str: Concatenated text of the top-3 most relevant documents separated by newlines.
             Returns a default message if the vector store is empty.
    
    Note:
        - Returns up to 3 results (hardcoded k=3, change in vector_store.search() if needed)
        - Returns empty context message if no documents have been indexed yet
        - Search uses L2 distance metric for similarity
    
    Example:
        >>> context = retrieve_context("How should authentication work?")
        >>> print(context)
        "Authentication must be OAuth 2.0 compliant...
         Users should log in with email and password..."
    """
    # Return placeholder if vector store is empty
    if len(vector_store.texts) == 0:
        return "No context available."
    
    # Encode the query and search for similar documents
    query_embedding = embed([query])
    results = vector_store.search(query_embedding, k=3)
    
    # Join results with newlines for readability in prompts
    return "\n".join(results)