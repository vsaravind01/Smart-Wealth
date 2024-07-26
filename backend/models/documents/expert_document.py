from datetime import datetime
from typing import List, Any
from backend.models.documents import BaseTextDocument, BaseDocumentMeta


class ExpertDocumentMeta(BaseDocumentMeta):
    title: str
    source: str
    date_published: datetime
    description: str
    summary: str
    companies: List[str]
    segments: List[str]
    news_sentiment: dict[str, float]
    market_trend: str
    keywords: List[str]


class ExpertDocument(BaseTextDocument):
    document_meta: ExpertDocumentMeta

    def __init__(self, /, **data: Any):
        super().__init__(**data)

    def format_document(self):
        return self.page_content
