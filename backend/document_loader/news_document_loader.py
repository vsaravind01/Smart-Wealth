from __future__ import annotations

import json
from os import PathLike
from typing import Optional

from backend.document_loader.base_document_loader import BaseTextDocumentLoader
from backend.models.documents.news_document import NewsDocument
from backend.models.documents.news_document import NewsBaseDocumentMeta


class NewsDocumentLoader(BaseTextDocumentLoader):
    """News DataLoader class. Used to parse web-scraped."""

    def __init__(self, file_path: PathLike, tag_set: Optional[list]):
        self.file_path = file_path

        super().__init__(tag_set)

        self._initialize()

    def _initialize(self):
        """Initialize by loading the dataset"""

        with open(self.file_path, "r") as file:
            ds = json.load(file)
            self._load_dataset(ds)

    def _load_dataset(self, dataset: list[dict]):
        """load the documents from the json dataset"""

        for doc in dataset:
            metadata = NewsBaseDocumentMeta(
                id=doc["id"],
                author_name=doc["author_name"],
                company_name=doc["company_name"],
                keywords=doc["keywords"],
                headline=doc["headline"],
                news_sentiment=doc["news_sentiment"],
                market_trend=doc["market_trend"],
                sector=doc["sector"],
                summary=doc["summary"],
                date_published=doc["date_published"],
                source=doc["source"],
                tags=doc["article_tags"],
                is_ai_generated=True,
            )
            document = NewsDocument(
                page_content=doc["page_content"], document_meta=metadata
            )
            self.documents.append(document)
