from typing import Any, Optional

from backend.models.documents import BaseTextDocument, BaseDocumentMeta


class WebsiteBaseDocumentMeta(BaseDocumentMeta):
    title: str
    description: Optional[str] = None
    referrer_source: Optional[str] = None


class WebsiteDocument(BaseTextDocument):
    document_meta: WebsiteBaseDocumentMeta

    def __init__(self, /, **data: Any):
        super().__init__(**data)

    def format_document(self):
        return self.page_content
