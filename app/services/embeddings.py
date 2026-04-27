"""
Text Embedding Service

This module handles the conversion of text documents to dense vector representations
using a pre-trained sentence transformer model. These embeddings enable semantic
similarity searches for retrieval-augmented generation (RAG).

Model: all-MiniLM-L6-v2
- Output dimension: 384
- Purpose: Lightweight, efficient semantic embeddings for similarity search
"""

from sentence_transformers import SentenceTransformer

# Load the pre-trained sentence transformer model once at module initialization
# This model is optimized for semantic similarity tasks and has a 384-dimensional output
model = SentenceTransformer('all-MiniLM-L6-v2')


def embed(texts):
    """
    Convert a list of text documents to semantic vector embeddings.
    
    Encodes texts using the pre-trained sentence transformer model, generating
    384-dimensional vectors that capture semantic meaning. These vectors can be
    used for similarity search in the vector store.
    
    Args:
        texts (list): List of text documents to embed.
                     Each item should be a string.
    
    Returns:
        np.ndarray: Array of embeddings with shape (len(texts), 384).
                   Each row is a semantic vector representation of the corresponding text.
    
    Example:
        >>> embeddings = embed(["How to build a system?", "System architecture design"])
        >>> print(embeddings.shape)
        (2, 384)
    """
    return model.encode(texts, show_progress_bar=False)