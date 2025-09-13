import faiss, numpy as np

EMB_PATH = "data/embeddings.npy"
INDEX_PATH = "data/faiss_index.bin"

emb = np.load(EMB_PATH)
index = faiss.IndexFlatIP(emb.shape[1])
index.add(emb.astype(np.float32))
faiss.write_index(index, INDEX_PATH)
print("FAISS Index geschrieben:", INDEX_PATH)
