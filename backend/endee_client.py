import json
import os
import numpy as np
try:
    from store import VectorStore
except ImportError:
    from backend.store import VectorStore

class EndeeClient:
    def __init__(self, base_url="http://localhost:8080", auth_token=None):
        self.store = VectorStore()
        print("DEBUG: Using local VectorStore simulation")

    def create_collection(self, name, dimension, metric="cosine"):
        return self.store.create_collection(name, dimension)

    def add_vectors(self, collection_name, ids, vectors, metadata=None):
        return self.store.add_vectors(collection_name, ids, vectors, metadata)

    def search(self, collection_name, vector, limit=5, filter_query=None):
        return self.store.search(collection_name, vector, limit)

    def list_collections(self):
        # Format expected by new app.py
        indexes = []
        for name, data in self.store.collections.items():
            indexes.append({
                "name": name,
                "total_elements": len(data)
            })
        return {"indexes": indexes}

    def check_health(self):
        return True
