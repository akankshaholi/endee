import requests
import json

class EndeeClient:
    def __init__(self, base_url="http://localhost:8080", auth_token="endee_token"):
        self.base_url = base_url
        self.headers = {"Authorization": auth_token, "Content-Type": "application/json"}

    def check_health(self):
        try:
            r = requests.get(f"{self.base_url}/api/v1/health", headers=self.headers)
            return r.status_code == 200
        except:
            return False

    def create_collection(self, name, dimension=384):
        data = {"name": name, "dimension": dimension, "metric": "cosine", "capacity": 1000}
        r = requests.post(f"{self.base_url}/api/v1/index/create", json=data, headers=self.headers)
        return r.json()

    def delete_collection(self, name):
        r = requests.delete(f"{self.base_url}/api/v1/index/{name}/delete", headers=self.headers)
        return r.json()

    def add_vectors(self, collection, ids, vectors, metadata=None):
        payload = {"ids": ids, "vectors": vectors}
        if metadata:
            payload["metadata"] = [json.dumps(m) for m in metadata]
        
        r = requests.post(f"{self.base_url}/api/v1/index/{collection}/add", json=payload, headers=self.headers)
        return r.json()

    def search(self, collection, vector, limit=10):
        payload = {"vector": vector, "limit": limit}
        r = requests.post(f"{self.base_url}/api/v1/index/{collection}/search", json=payload, headers=self.headers)
        return r.json()
