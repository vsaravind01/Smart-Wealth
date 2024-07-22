from typing import Any, List, Optional
from datetime import datetime
from pydantic import HttpUrl

from backend.models.documents import BaseTextDocument, BaseDocumentMeta


class NewsBaseDocumentMeta(BaseDocumentMeta):
    id: str
    author_name: str
    company_name: str
    keywords: List[str]
    link: HttpUrl
    headline: str
    news_sentiment: dict
    market_trend: str
    sector: str
    summary: str
    date_published: datetime


class NewsDocument(BaseTextDocument):
    news_meta: NewsBaseDocumentMeta

    def __init__(self, /, **data: Any):
        self.news_meta = NewsBaseDocumentMeta(**data)

    def format_document(self):
        return self.page_content
