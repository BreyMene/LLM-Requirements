"""
Vector Store Module for FAISS-based Semantic Search

This module provides a persistent vector database using FAISS (Facebook AI Similarity Search).
It stores text embeddings and their associated source documents, enabling efficient semantic
similarity search for retrieval-augmented generation (RAG) workflows.
"""

import faiss
import numpy as np
import os


class VectorStore:
    """
    A wrapper class for FAISS vector indexing with persistence.
    
    Attributes:
        index (faiss.IndexFlatL2): FAISS index for storing and searching embeddings.
        texts (list): List of original text documents corresponding to embeddings.
        metadatas (list): List of JSON metadata objects aligned with texts.
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
        self.metadatas = []

    def add(self, embeddings, texts, metadatas=None):
        """
        Add new document embeddings to the vector store while preventing duplicates.
        
        Args:
            embeddings (np.ndarray or list): Vector embeddings of shape (n_docs, dim).
            texts (list): List of text documents corresponding to embeddings.
                         Must have same length as embeddings.
            metadatas (list, optional): List of metadata objects for each document.
                         If provided, must have same length as texts.
        
        Returns:
            None: Modifies the index, texts, and metadatas in-place.
        """
        new_texts = []
        new_metadatas = []

        # Filter out duplicate texts to avoid redundancy
        for idx, t in enumerate(texts):
            if t not in self.texts:
                new_texts.append(t)
                if metadatas is not None and idx < len(metadatas):
                    new_metadatas.append(metadatas[idx])
                else:
                    new_metadatas.append({})

        if not new_texts:
            return

        # Convert embeddings to float32 format required by FAISS
        embeddings = np.array(embeddings).astype('float32')

        # Add only embeddings for new texts
        self.index.add(embeddings[:len(new_texts)])
        self.texts.extend(new_texts)
        self.metadatas.extend(new_metadatas)

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
            - {path}/metadata.json: JSON metadata list for each stored text chunk
        
        Returns:
            None
        """
        os.makedirs(path, exist_ok=True)
        faiss.write_index(self.index, f"{path}/index.faiss")
        metadata_items = [
            {"text": text, "metadata": metadata}
            for text, metadata in zip(self.texts, self.metadatas)
        ]
        with open(f"{path}/metadata.json", "w", encoding="utf-8") as f:
            import json
            json.dump(metadata_items, f, ensure_ascii=False, indent=2)

    def load(self, path="vectorstore"):
        """
        Load a previously saved index and metadata from disk.
        
        Attempts to load the FAISS index and document metadata from the specified path.
        Silently fails if files don't exist (useful for first-time initialization).
        
        Args:
            path (str, optional): Directory path containing index and metadata files.
                                Defaults to "vectorstore".
        
        Returns:
            None: Modifies index, texts, and metadatas in-place.
        
        Note:
            If loading fails, the store retains its current state without raising errors.
        """
        try:
            self.index = faiss.read_index(f"{path}/index.faiss")
            if os.path.exists(f"{path}/metadata.json"):
                with open(f"{path}/metadata.json", "r", encoding="utf-8") as f:
                    import json
                    metadata_items = json.load(f)
                    self.texts = [item.get("text", "") for item in metadata_items]
                    self.metadatas = [item.get("metadata", {}) for item in metadata_items]
        except Exception:
            # Silently fail - useful for first initialization when files don't exist yet
            pass