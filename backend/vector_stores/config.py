from typing import Type

from backend.models.documents import (
    BaseDocument,
    NewsDocument,
    ExpertDocument,
    WebsiteDocument,
    FaqDocument,
    MutualFundDocument,
)


class DocumentContainer:
    def __init__(self, document_class: Type[BaseDocument], columns: list[str]):
        self.document_class = document_class
        self.columns = columns


container_to_document_map: dict[str, DocumentContainer] = {
    "stock-news": DocumentContainer(NewsDocument, ["document_meta", "page_content"]),
    "expert-news": DocumentContainer(ExpertDocument, ["document_meta", "page_content"]),
    "bob-web": DocumentContainer(WebsiteDocument, ["document_meta", "page_content"]),
    "mutual-fund": DocumentContainer(MutualFundDocument, ["document_meta"]),
    "faq": DocumentContainer(FaqDocument, ["document_meta", "question", "answer"]),
}
