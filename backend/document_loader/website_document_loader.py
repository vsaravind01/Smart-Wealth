from __future__ import annotations

import json
from os import PathLike
from typing import Optional

from backend.document_loader.base_document_loader import BaseTextDocumentLoader
from backend.models.documents import (
    WebsiteDocument,
    WebsiteBaseDocumentMeta,
    FaqDocument,
    FaqBaseDocumentMeta,
)
from backend.models.documents.tags import tags

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)


class WebsiteDocumentLoader(BaseTextDocumentLoader[WebsiteDocument]):
    """Website DataLoader class. Used to parse web-scraped."""

    def __init__(self, file_path: str | PathLike, tag_set: Optional[list] = None):
        self.faqs = []
        self.file_path = file_path
        if not tag_set:
            tag_set = tags

        super().__init__(tag_set)

        self._initialize()

    def _initialize(self):
        """Initialize by loading the dataset and faqs with tags"""
        with open(self.file_path, "r") as file:
            ds = json.load(file)
            self._load_documents(ds)
            self._load_faqs(ds)
            tag_fields = [["document_meta", "source"], ["document_meta", "title"]]
            self.set_tags(self.documents, tag_fields=tag_fields)
            self.set_tags(self.faqs, tag_fields=tag_fields, must_tags=["faq"])

    def _load_documents(self, dataset: list[dict]):
        """load the documents from the json dataset"""

        def good_url(url: str):
            return not any(
                [
                    url.endswith("articles"),
                    url.startswith(
                        "https://www.bankofbaroda.in/personal-banking/offers"
                    ),
                    url.startswith("https://www.bankofbaroda.in/media/news-coverage"),
                    url.startswith(
                        "https://www.bankofbaroda.in/shareholders-corner/disclosures-under-sebi-listing-regulations"
                    ),
                    url.startswith("https://www.bankofbaroda.in/banking-mantra/videos"),
                    url.startswith("https://www.bankofbaroda.in/contact-us"),
                    "weekly-wrap" in url,
                    "newsletter-fintalk" in url,
                    url == "https://www.bankofbaroda.in/",
                    url
                    == "https://www.bankofbaroda.in/customer-support/code-for-collection-of-dues-and-repossession-of-security",
                ]
            )

        for doc in dataset:
            if good_url(doc["url"]):
                metadata = WebsiteBaseDocumentMeta(
                    source=doc["url"],
                    referrer_source=doc["crawl"]["referrerUrl"],
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
                                referrer_source=d["crawl"]["referrerUrl"],
                            )
                            document = FaqDocument(
                                question=faq_meta["name"],
                                answer=faq_meta["acceptedAnswer"]["text"],
                                document_meta=metadata,
                            )
                            self.faqs.append(document)

    def split_documents(self, **kwargs):
        def should_ignore(_document: WebsiteDocument):
            _size = len(_document.page_content.split(" "))
            conditions_to_ignore = [
                _document.document_meta.source.endswith("articles"),
                _document.document_meta.source.startswith(
                    "https://www.bankofbaroda.in/personal-banking/offers"
                ),
                _document.document_meta.source == "https://www.bankofbaroda.in/",
                _size > 20000,
                _size < 25,
            ]
            return any(conditions_to_ignore)

        headers_to_split_on = kwargs.get(
            "headers_to_split_on",
            [
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ],
        )

        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            return_each_line=True,
            strip_headers=False,
        )
        docs = []
        for document in self.documents:
            size = len(document.page_content.split(" "))
            if should_ignore(document):
                continue
            elif size > 1024:
                documents = markdown_splitter.split_text(document.page_content)
                temp_documents = []
                for temp_document in documents:
                    if len(temp_document.page_content.split(" ")) < 25:
                        continue
                    elif len(temp_document.page_content.split(" ")) > 1600:
                        char_splitter = RecursiveCharacterTextSplitter(chunk_size=1500)
                        ds = char_splitter.split_text(temp_document.page_content)
                        for d in ds:
                            temp_documents.append(
                                WebsiteDocument(
                                    page_content=d, document_meta=document.document_meta
                                )
                            )
                    else:
                        temp_documents.append(
                            WebsiteDocument(
                                page_content=temp_document.page_content,
                                document_meta=document.document_meta,
                            )
                        )
                documents = temp_documents
            else:
                documents = [document]
            docs.extend(documents)

        return docs

    @staticmethod
    def format_document(document: WebsiteDocument):
        return document.page_content
