from __future__ import annotations

import json
from os import PathLike
from typing import Optional

from backend.document_loader.base_document_loader import BaseDocumentLoader
from backend.models.documents.expert_document import ExpertDocument
from backend.models.documents.expert_document import ExpertDocumentMeta


class ExpertDocumentLoader(BaseDocumentLoader):
    """Expert DataLoader class. Used to parse web-scraped."""

    def __init__(self, file_path: PathLike, tag_set: Optional[list]):
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
                time=doc["time"],
                author=doc["author"],
                description=doc["description"],
                company=doc["company"],
                type=doc["type"],
                last_updated_time=doc["last_updated_time"],
                link=doc["link"],
            )
            document = ExpertDocument(
                page_content=doc["content"], document_meta=metadata
            )
            self.documents.append(document)
