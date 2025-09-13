import os, json, httpx, numpy as np, faiss
from typing import List
from .models import QueryRequest, QueryResponse, Card
from .intents import detect_intent
import typesense
from sentence_transformers import SentenceTransformer

# Typesense Client
ts = typesense.Client({
  'nodes': [{ 'host': os.getenv('TYPESENSE_HOST','localhost'), 'port': int(os.getenv('TYPESENSE_PORT','8108')), 'protocol': 'http' }],
  'api_key': os.getenv('TYPESENSE_API_KEY','changeme'),
  'connection_timeout_seconds': 5
})

# FAISS + Embeddings
EMB_MODEL = os.getenv('EMBED_MODEL','sentence-transformers/all-MiniLM-L6-v2')
EMB_PATH = 'data/embeddings.npy'
META_PATH = 'data/meta.jsonl'
INDEX_PATH = 'data/faiss_index.bin'
model = SentenceTransformer(EMB_MODEL)
faiss_index = faiss.read_index(INDEX_PATH)
meta = [json.loads(l) for l in open(META_PATH, encoding='utf-8')]

async def search_typesense(q: str, top_k=5) -> List[Card]:
    r = ts.collections['pages'].documents.search({
        'q': q,
        'query_by': 'title,content',
        'per_page': top_k
    })
    cards = []
    for h in r.get('hits', []):
        doc = h['document']
        cards.append(Card(title=doc['title'], url=doc['url'], snippet=(doc['content'] or '')[:300]))
    return cards

async def search_faiss(q: str, top_k=5) -> List[Card]:
    qv = model.encode([q], normalize_embeddings=True)
    D, I = faiss_index.search(np.array(qv, dtype='float32'), top_k)
    cards = []
    for idx, score in zip(I[0], D[0]):
        m = meta[idx]
        cards.append(Card(title=m['title'], url=m['url'], snippet=f"Relevanz {score:.2f}"))
    # Dedupliziere per URL
    seen, dedup = set(), []
    for c in cards:
        if c.url not in seen:
            dedup.append(c); seen.add(c.url)
    return dedup

async def llm_answer(query: str, context: str) -> str | None:
    host = os.getenv('OLLAMA_HOST')
    model = os.getenv('OLLAMA_MODEL')
    if not host or not model:
        return None
    prompt = (
        "Beantworte kurz und praezise auf Deutsch (Schweiz). Nutze NUR den Kontext. "
        "Fuege am Ende KEINE neuen Links hinzu.\n\n"
        f"Frage: {query}\n\nKontext:\n{context}"
    )
    try:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(f"{host}/api/generate", json={"model": model, "prompt": prompt})
            r.raise_for_status()
            return r.text.strip()
    except Exception:
        return None

async def handle_query(q: str, top_k=5) -> QueryResponse:
    intent = detect_intent(q)
    if intent in {"kontakt","termin"}:
        cards = await search_typesense("kontakt")
        return QueryResponse(intent=intent, cards=cards[:3])
    cards_kw = await search_typesense(q, top_k=top_k)
    cards_vec = await search_faiss(q, top_k=top_k)
    merged, seen = [], set()
    for c in cards_kw + cards_vec:
        if c.url not in seen:
            merged.append(c); seen.add(c.url)
    context = "\n\n".join(c.snippet for c in merged[:3])
    answer = await llm_answer(q, context)
    return QueryResponse(intent=intent, cards=merged[:5], answer=answer)
