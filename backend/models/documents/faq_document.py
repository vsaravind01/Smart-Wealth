from typing import Any, Optional

from backend.models.documents import BaseDocument, BaseDocumentMeta


class FaqBaseDocumentMeta(BaseDocumentMeta):
    title: str

    referrer_source: Optional[str] = None


class FaqDocument(BaseDocument):
    question: str
    answer: str

    document_meta: FaqBaseDocumentMeta

    def __init__(self, /, **data: Any):
        super().__init__(**data)
