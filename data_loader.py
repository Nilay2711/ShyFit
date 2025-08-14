
import json
import faiss
import os
from sentence_transformers import SentenceTransformer
import numpy as np

DATASET_PATH = "Y:/Future Stuff and All/ShyFit/final_dataset_cleaned.jsonl"
INDEX_PATH = "Y:/Future Stuff and All/ShyFit/faiss.index"
META_PATH = "Y:/Future Stuff and All/ShyFit/metadata.json"

def load_jsonl(path):
    data = []
    with open(path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"JSON parse error at line {i}: {e}")
    return data


def embed_dataset(model_name="all-MiniLM-L6-v2"):
    dataset = load_jsonl("Y:/Future Stuff and All/ShyFit/final_dataset_cleaned.jsonl")
    model = SentenceTransformer(model_name)

    texts = []
    cleaned_data = []

    for i, entry in enumerate(dataset):
        try:
            goal = entry["goal"]
            muscles = ' '.join(entry["target_muscles"])
            level = entry["level"]
            duration = str(entry["duration_minutes"])

            text = f"{goal} {muscles} {level} {duration}"
            texts.append(text)
            cleaned_data.append(entry)

        except KeyError as e:
            print(f"Skipping entry #{i} — missing key: {e}")
            continue

    print(f"\nEmbedding {len(texts)} valid entries...")

    embeddings = model.encode(texts, convert_to_numpy=True)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, "Y:/Future Stuff and All/ShyFit/faiss.index")
    with open("Y:/Future Stuff and All/ShyFit/metadata.json", "w", encoding='utf-8') as f:
        json.dump(cleaned_data, f)



if __name__ == "__main__":
    embed_dataset()
