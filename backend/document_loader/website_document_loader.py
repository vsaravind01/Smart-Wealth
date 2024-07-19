from __future__ import annotations

import json
from os import PathLike
from typing import Optional

from backend.document_loader.base_document_loader import BaseDataLoader

from backend.models.documents import (
    WebsiteDocument,
    WebsiteBaseDocumentMeta,
    FaqDocument,
    FaqBaseDocumentMeta,
)


class WebsiteDataLoader(BaseDataLoader):
    """Website DataLoader class. Used to parse web-scraped."""

    def __init__(self, file_path: PathLike, tag_set: Optional[list]):
        self.faqs = []
        self.file_path = file_path

        super().__init__(tag_set)

        self._initialize()

    def _initialize(self):
        """Initialize by loading the dataset and faqs with tags"""
        with open(self.file_path, "r") as file:
            ds = json.load(file)
            self._load_dataset(ds)
            self._load_faqs(ds)
            self.set_tags(self.documents)
            self.set_tags(self.faqs, must_tags=["faq"])

    def _load_dataset(self, dataset: list[dict]):
        """load the documents from the json dataset"""
        for doc in dataset:
            metadata = WebsiteBaseDocumentMeta(
                source=doc["url"],
                referred_source=doc["crawl"]["referredUrl"],
                title=doc["metadata"]["title"],
                description=doc["metadata"]["description"],
            )
            document = WebsiteDocument(
                page_content=doc["markdown"], document_meta=metadata
            )
            self.documents.append(document)

    def _load_faqs(self, dataset: list[dict]):
        """load the faqs from the json dataset"""
        for d in dataset:
            if "jsonLd" in d["metadata"]:
                for j in d["metadata"]["jsonLd"]:
                    if j["@type"] == "FAQPage":
                        for faq_meta in j["mainEntity"]:
                            metadata = FaqBaseDocumentMeta(
                                title=d["metadata"]["title"],
                                source=d["url"],
                                referred_source=d["crawl"]["referredUrl"],
                            )
                            document = FaqDocument(
                                question=faq_meta["name"],
                                answer=faq_meta["acceptedAnswer"]["text"],
                                document_meta=metadata,
                            )
                            self.faqs.append(document)