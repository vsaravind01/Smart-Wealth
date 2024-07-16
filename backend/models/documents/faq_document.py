from typing import Any, Optional

from backend.models.documents import BaseDocument, DocumentMeta


class FaqDocumentMeta(DocumentMeta):
    title: str

    referred_source: Optional[str] = None


class FaqDocument(BaseDocument):
    question: str
    answer: str

    document_meta: FaqDocumentMeta

    def __init__(self, /, **data: Any):
        super().__init__(**data)
