from typing import Any, Optional

from backend.models.documents import BaseTextDocument, BaseDocumentMeta


class WebsiteBaseDocumentMeta(BaseDocumentMeta):
    title: str
    source_map: Optional[str] = None
    description: Optional[str] = None
    referrer_source: Optional[str] = None


class WebsiteDocument(BaseTextDocument):
    document_meta: WebsiteBaseDocumentMeta

    def __init__(self, /, **data: Any):
        super().__init__(**data)

    def format_document(self):
        if len(self.page_content.split(" ")) > 100:
            return self.page_content
        else:
            return f"{self.document_meta.description}\n\n{self.page_content}"
