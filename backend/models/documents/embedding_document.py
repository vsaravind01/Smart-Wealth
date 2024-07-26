from __future__ import annotations

from pydantic import BaseModel
from typing import List, Optional
from backend.models.documents import NewsDocument, ExpertDocument, WebsiteDocument


class EmbeddingDocument(BaseModel):
    document: NewsDocument | ExpertDocument | WebsiteDocument
    similarity_score: float

    embedding: Optional[List[float]] = None
