from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    q: str
    top_k: int = 5

class Card(BaseModel):
    title: str
    url: str
    snippet: str
    cta: str = "Ansehen"

class QueryResponse(BaseModel):
    intent: str
    cards: List[Card]
    answer: Optional[str] = None
