from __future__ import annotations

import json
from os import PathLike
from typing import Optional

from backend.document_loader.base_document_loader import BaseTextDocumentLoader
from backend.models.documents.expert_document import ExpertDocument
from backend.models.documents.expert_document import ExpertDocumentMeta


class ExpertDocumentLoader(BaseTextDocumentLoader[ExpertDocument]):
    """Expert DataLoader class. Used to parse web-scraped."""

    def __init__(self, file_path: PathLike | str, tag_set: Optional[list] = None):
        self.file_path = file_path

        super().__init__(tag_set)

        self._initialize()

    def _initialize(self):
        """Initialize by loading the dataset"""
        with open(self.file_path, "r") as file:
            ds = json.load(file)
            self._load_documents(ds)

    def _load_documents(self, dataset: list[dict]):
        """load the documents from the json dataset"""

        for doc in dataset:
            metadata = ExpertDocumentMeta(
                title=doc["title"],
                source=doc["source"],
                date_published=doc["date_published"],
                description=doc["Description"],
                summary=doc["summary"],
                companies=doc["company_name"],
                news_sentiment=doc["news_sentiment"],
                market_trend=doc["market_trend"],
                segments=doc["segment"],
                keywords=doc["keywords"],
            )
            document = ExpertDocument(
                page_content=doc["page_content"], document_meta=metadata
            )
            self.documents.append(document)
