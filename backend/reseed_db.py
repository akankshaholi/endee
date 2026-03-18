from endee_client import EndeeClient
from sentence_transformers import SentenceTransformer
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

ENDEE_URL = os.getenv("ENDEE_URL", "http://localhost:8080")
ENDEE_TOKEN = os.getenv("ENDEE_TOKEN", "endee_token")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "food_items")

client = EndeeClient(base_url=ENDEE_URL, auth_token=ENDEE_TOKEN)
model = SentenceTransformer('all-MiniLM-L6-v2')

def seed():
    print("Seeding database...")
    
    # Clean up existing data first
    try:
        client.delete_collection(COLLECTION_NAME)
        print("Cleared old data.")
    except:
        pass

    time.sleep(1)

    # Create collection
    client.create_collection(COLLECTION_NAME, dimension=384)
    print(f"Created collection: {COLLECTION_NAME}")

    # Load samples
    data_path = os.path.join(os.path.dirname(__file__), '../data/sample_data.json')
    with open(data_path, 'r') as f:
        food_items = json.load(f)

    # Generate vectors
    print(f"Encoding {len(food_items)} dishes...")
    ids = [item['id'] for item in food_items]
    texts = [f"{item['name']} {item['description']} {item['cuisine']}" for item in food_items]
    embeddings = model.encode(texts)

    # Store in Endee
    client.add_vectors(COLLECTION_NAME, ids, embeddings.tolist(), metadata=food_items)
    print("Done! Endee is ready with data.")

if __name__ == "__main__":
    seed()
