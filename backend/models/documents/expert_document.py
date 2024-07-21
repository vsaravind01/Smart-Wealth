from datetime import datetime
from typing import List, Any
from pydantic import HttpUrl
from backend.models.documents import BaseDocument, BaseDocumentMeta


class ExpertDocumentMeta(BaseDocumentMeta):
    title: str
    source: str
    time: datetime
    author: str
    content: str
    description: str
    company: List[str]
    type: str
    last_updated_time: datetime
    link: HttpUrl


class ExpertDocument(BaseDocument):
    document_meta: ExpertDocumentMeta

    def __init__(self, /, **data: Any):
        super().__init__(**data)
