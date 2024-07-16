from typing import Any, Optional

from backend.models.documents import BaseTextDocument, DocumentMeta


class WebsiteDocumentMeta(DocumentMeta):
    title: str
    description: Optional[str] = None
    referrer_source: Optional[str] = None


class WebsiteDocument(BaseTextDocument):
    document_meta: WebsiteDocumentMeta

    def __init__(self, /, **data: Any):
        super().__init__(**data)
