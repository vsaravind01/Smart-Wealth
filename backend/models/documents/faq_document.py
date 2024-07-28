from typing import Any, Optional

from backend.models.documents import BaseDocument, BaseDocumentMeta


class FaqBaseDocumentMeta(BaseDocumentMeta):
    title: str
    source_map: Optional[str] = None

    referrer_source: Optional[str] = None


class FaqDocument(BaseDocument):
    question: str
    answer: str

    document_meta: FaqBaseDocumentMeta

    def __init__(self, /, **data: Any):
        super().__init__(**data)

    def format_document(self):
        return f"{self.question}\n\n{self.answer}"
