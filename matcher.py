
import faiss
import json
import numpy as np
import sys
from sentence_transformers import SentenceTransformer
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "data", "faiss.index")
META_PATH = os.path.join(BASE_DIR, "data", "metadata.json")


# Cache model to avoid loading on every call
_model_cache = {}

def get_model(model_name):
    if model_name not in _model_cache:
        _model_cache[model_name] = SentenceTransformer(model_name)
    return _model_cache[model_name]

def load_index():
    return faiss.read_index(INDEX_PATH)

def load_metadata():
    with open(META_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def search_workouts(query, top_k=3, model_name="all-MiniLM-L6-v2"):
    model = get_model(model_name)
    query_vec = model.encode([query]).astype('float32')

    index = load_index()
    metadata = load_metadata()

    D, I = index.search(query_vec, top_k)

    results = []
    for i in I[0]:
        if 0 <= i < len(metadata):
            results.append(metadata[i])
        else:
            print(f"[WARN] Index {i} out of bounds for metadata size {len(metadata)}")

    return results

if __name__ == "__main__":
    # CLI usage: python matcher.py [your query here...]
    if len(sys.argv) < 2:
        query = input("Enter your workout query: ")
    else:
        query = " ".join(sys.argv[1:])

    matches = search_workouts(query)

    for idx, match in enumerate(matches, 1):
        print(f"\n--- Match {idx} ---")
        print(json.dumps(match, indent=2, ensure_ascii=False))
