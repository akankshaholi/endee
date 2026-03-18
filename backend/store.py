import json
import os
import numpy as np

class VectorStore:
    def __init__(self, storage_path="vector_store.json"):
        self.storage_path = storage_path
        self.collections = {}
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                try:
                    self.collections = json.load(f)
                except:
                    self.collections = {}

    def _save(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.collections, f, indent=2)

    def create_collection(self, name, dimension):
        if name not in self.collections:
            self.collections[name] = []
            self._save()
        return {"status": "success"}

    def add_vectors(self, collection_name, ids, vectors, metadata=None):
        if collection_name not in self.collections:
            self.collections[collection_name] = []
        
        for i, vid in enumerate(ids):
            meta = metadata[i] if metadata and i < len(metadata) else {}
            entry = {
                "id": str(vid),
                "vector": vectors[i],
                "meta": json.dumps(meta) if isinstance(meta, dict) else meta
            }
            self.collections[collection_name].append(entry)
        self._save()
        return {"status": "success"}

    def search(self, collection_name, query_vector, k=5):
        if collection_name not in self.collections:
            return {"results": []}
        
        results = []
        q_vec = np.array(query_vector)
        
        for item in self.collections[collection_name]:
            i_vec = np.array(item["vector"])
            # Cosine similarity
            sim = np.dot(q_vec, i_vec) / (np.linalg.norm(q_vec) * np.linalg.norm(i_vec) + 1e-9)
            results.append({
                "score": float(sim),
                "id": item["id"],
                "meta": item["meta"]
            })
            
        results.sort(key=lambda x: x["score"], reverse=True)
        return {"results": results[:k]}
