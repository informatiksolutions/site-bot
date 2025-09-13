import json, os
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
DATA = "data/chunks.jsonl"
EMB_PATH = "data/embeddings.npy"

def main():
    model = SentenceTransformer(MODEL)
    texts, meta = [], []
    with open(DATA, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            texts.append(rec["content"])
            meta.append({k: rec[k] for k in ("id","url","title")})
    emb = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    np.save(EMB_PATH, emb)
    with open("data/meta.jsonl","w",encoding="utf-8") as m:
        for r in meta:
            m.write(json.dumps(r, ensure_ascii=False)+"\n")
    print("Embeddings gespeichert:", emb.shape)

if __name__ == "__main__":
    main()
