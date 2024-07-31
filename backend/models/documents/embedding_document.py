from __future__ import annotations

from pydantic import BaseModel
from typing import List, Optional
from backend.models.documents import BaseDocument


class ResponseDocument(BaseModel):
    document: BaseDocument
    similarity_score: float

    embedding: Optional[List[float]] = None
