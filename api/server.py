from fastapi import FastAPI
from .models import QueryRequest
from .router import handle_query

app = FastAPI(title="Site Bot API")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/query")
async def query(req: QueryRequest):
    return await handle_query(req.q, req.top_k)
