"""
vector_database.py

Contains the VectorDatabase class for a simple "global brain" approach.
"""

import random
import numpy as np

class VectorDatabase:
    """
    Placeholder for unifying memory in a single semantic store (Faiss or Milvus).
    Currently just stores documents in a list and returns random samples.
    """

    def __init__(self):
        self.documents = []
        self.embeddings = []

    def add_document(self, text: str, embedding: np.ndarray):
        self.documents.append(text)
        self.embeddings.append(embedding)

    def search_similar(self, query_embedding: np.ndarray, top_k=3):
        # For now, just random
        if not self.documents:
            return []
        return random.sample(self.documents, min(len(self.documents), top_k))
