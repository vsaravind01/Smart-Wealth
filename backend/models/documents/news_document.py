from typing import Any, List, Optional
from datetime import datetime

from backend.models.documents import BaseTextDocument, BaseDocumentMeta


class NewsDocumentMeta(BaseDocumentMeta):
    author_name: str
    company_name: str
    keywords: List[str]
    headline: str
    news_sentiment: dict
    market_trend: str
    sector: str
    summary: str
    date_published: datetime
    ticker: Optional[str] = None


class NewsDocument(BaseTextDocument):
    document_meta: NewsDocumentMeta

    def __init__(self, /, **data: Any):
        super().__init__(**data)

    def format_document(self):
        return self.page_content
