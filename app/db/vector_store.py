"""
Vector Store Module for FAISS-based Semantic Search

This module provides a persistent vector database using FAISS (Facebook AI Similarity Search).
It stores text embeddings and their associated source documents, enabling efficient semantic
similarity search for retrieval-augmented generation (RAG) workflows.
"""

import faiss
import numpy as np
import pickle
import os


class VectorStore:
    """
    A wrapper class for FAISS vector indexing with persistence.
    
    Attributes:
        index (faiss.IndexFlatL2): FAISS index for storing and searching embeddings.
        texts (list): List of original text documents corresponding to embeddings.
        dim (int): Dimension of embeddings (default: 384 for all-MiniLM-L6-v2).
    """

    def __init__(self, dim=384):
        """
        Initialize a new vector store with a flat L2 distance index.
        
        Args:
            dim (int, optional): Dimensionality of embeddings. Defaults to 384,
                               which matches the all-MiniLM-L6-v2 model output.
        """
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []

    def add(self, embeddings, texts):
        """
        Add new document embeddings to the vector store while preventing duplicates.
        
        Args:
            embeddings (np.ndarray or list): Vector embeddings of shape (n_docs, dim).
            texts (list): List of text documents corresponding to embeddings.
                         Must have same length as embeddings.
        
        Returns:
            None: Modifies the index and texts in-place.
        """
        new_texts = []

        # Filter out duplicate texts to avoid redundancy
        for t in texts:
            if t not in self.texts:
                new_texts.append(t)

        if not new_texts:
            return

        # Convert embeddings to float32 format required by FAISS
        embeddings = np.array(embeddings).astype('float32')

        # Add only embeddings for new texts
        self.index.add(embeddings[:len(new_texts)])
        self.texts.extend(new_texts)

    def search(self, query_embedding, k=3):
        """
        Search the vector store for the k most similar documents.
        
        Uses L2 distance metric to find semantically similar documents to the query.
        
        Args:
            query_embedding (np.ndarray): Single embedding vector of shape (1, dim).
            k (int, optional): Number of top results to return. Defaults to 3.
        
        Returns:
            list: List of up to k text documents ranked by similarity (most similar first).
                 Returns fewer results if index has fewer than k documents.
        """
        D, I = self.index.search(query_embedding, k)
        return [self.texts[i] for i in I[0] if i < len(self.texts)]

    def save(self, path="vectorstore"):
        """
        Persist the index and metadata to disk.
        
        Saves the FAISS index and document texts to enable loading in future sessions.
        Creates the directory if it doesn't exist.
        
        Args:
            path (str, optional): Directory path for storing index and metadata files.
                                Defaults to "vectorstore".
        
        Files created:
            - {path}/index.faiss: Binary FAISS index
            - {path}/metadata.pkl: Pickled list of text documents
        
        Returns:
            None
        """
        os.makedirs(path, exist_ok=True)
        faiss.write_index(self.index, f"{path}/index.faiss")
        with open(f"{path}/metadata.pkl", "wb") as f:
            pickle.dump(self.texts, f)

    def load(self, path="vectorstore"):
        """
        Load a previously saved index and metadata from disk.
        
        Attempts to load the FAISS index and document texts from the specified path.
        Silently fails if files don't exist (useful for first-time initialization).
        
        Args:
            path (str, optional): Directory path containing index and metadata files.
                                Defaults to "vectorstore".
        
        Returns:
            None: Modifies index and texts in-place.
        
        Note:
            If loading fails, the store retains its current state without raising errors.
        """
        try:
            self.index = faiss.read_index(f"{path}/index.faiss")
            with open(f"{path}/metadata.pkl", "rb") as f:
                self.texts = pickle.load(f)
        except Exception:
            # Silently fail - useful for first initialization when files don't exist yet
            pass