from __future__ import annotations

import json
from os import PathLike
from typing import Optional

from backend.document_loader.base_document_loader import BaseTextDocumentLoader
from backend.models.documents.news_document import NewsDocument, NewsDocumentMeta


class NewsDocumentLoader(BaseTextDocumentLoader[NewsDocument]):
    """News DataLoader class. Used to parse web-scraped."""

    def __init__(self, file_path: PathLike | str, tag_set: Optional[list] = None):
        if not tag_set:
            tag_set = []
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
            metadata = NewsDocumentMeta(
                **doc["document_meta"],
            )
            document = NewsDocument(
                page_content=doc["page_content"], document_meta=metadata
            )
            self.documents.append(document)
