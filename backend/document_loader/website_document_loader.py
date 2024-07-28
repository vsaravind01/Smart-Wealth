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
from backend.models.documents.tags import web_tag_map
from backend.models.loader_utils.type_maps import SourceMap

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
)
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings


class WebsiteDocumentLoader(BaseTextDocumentLoader[WebsiteDocument]):
    """Website DataLoader class. Used to parse web-scraped."""

    def __init__(
        self,
        file_path: str | PathLike,
        tag_set: Optional[list] = None,
        source_map: Optional[SourceMap] = None,
        must_tags: Optional[list[str]] = None,
    ):
        if not must_tags:
            must_tags = []

        self.faqs: list[FaqDocument] = []
        self.file_path = file_path
        self.source_map = source_map
        self.must_tags = set(must_tags)
        if not tag_set:
            tag_set = list(web_tag_map.keys())
        tag_map = web_tag_map

        super().__init__(tag_set=tag_set, tag_map=tag_map)

        self._initialize()

    def _initialize(self):
        """Initialize by loading the dataset and faqs with tags"""
        with open(self.file_path, "r") as file:
            ds = json.load(file)
            self._load_documents(ds)
            self._load_faqs(ds)
            tag_fields = [
                ["document_meta", "source"],
                ["document_meta", "title"],
                ["document_meta", "description"],
            ]
            self.set_tags(
                self.documents, tag_fields=tag_fields, must_tags=self.must_tags
            )
            self.set_tags(self.faqs, tag_fields=tag_fields, must_tags=self.must_tags)

    def is_good_doc(
        self, check_document: dict, *, faq_enabled: Optional[bool] = False
    ) -> bool:
        """Check if the document is a good document"""
        if self.source_map:
            if check_document["url"].startswith(self.source_map.url_prefix):
                if "jsonLd" in check_document["metadata"]:
                    for j in check_document["metadata"]["jsonLd"]:
                        if j["@type"] == "FAQPage":
                            return faq_enabled
                return True
            else:
                return False
        return True

    def _load_documents(self, dataset: list[dict]):
        """load the documents from the json dataset"""
        for doc in dataset:
            if self.is_good_doc(doc, faq_enabled=True):
                for faq in self.faqs:
                    if faq.question in doc["markdown"]:
                        doc["markdown"] = doc["markdown"].replace(faq.question, "")
                    if faq.answer in doc["markdown"]:
                        doc["markdown"] = doc["markdown"].replace(faq.answer, "")
                metadata = WebsiteBaseDocumentMeta(
                    source=doc["url"],
                    referrer_source=doc["crawl"]["referrerUrl"],
                    title=doc["metadata"]["title"],
                    description=doc["metadata"]["description"],
                    source_map=self.source_map.value if self.source_map else None,
                )
                document = WebsiteDocument(
                    page_content=doc["markdown"], document_meta=metadata
                )
                self.documents.append(document)

    def _load_faqs(self, dataset: list[dict]) -> None:
        """load the faqs from the json dataset"""
        for d in dataset:
            if self.is_good_doc(d, faq_enabled=True):
                if "jsonLd" in d["metadata"]:
                    for j in d["metadata"]["jsonLd"]:
                        if j["@type"] == "FAQPage":
                            for faq_meta in j["mainEntity"]:
                                metadata = FaqBaseDocumentMeta(
                                    title=d["metadata"]["title"],
                                    source=d["url"],
                                    source_map=self.source_map.value,
                                    referrer_source=d["crawl"]["referrerUrl"],
                                )
                                document = FaqDocument(
                                    question=faq_meta["name"],
                                    answer=faq_meta["acceptedAnswer"]["text"],
                                    document_meta=metadata,
                                )
                                self.faqs.append(document)

    def split_documents(
        self,
        max_size_threshold: Optional[int] = 20000,
        min_size_threshold: Optional[int] = 25,
        sub_split_threshold: Optional[int] = 350,
        **kwargs,
    ) -> list[WebsiteDocument]:
        """Split WebsiteDocuments"""

        def should_ignore(_document: WebsiteDocument):
            _size = len(_document.page_content.split(" "))
            conditions_to_ignore = [
                _size > max_size_threshold,
                _size < min_size_threshold,
            ]
            return any(conditions_to_ignore)

        headers_to_split_on = kwargs.get(
            "headers_to_split_on",
            [
                ("#", "Header 1"),
                ("##", "Header 2"),
            ],
        )

        main_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            return_each_line=True,
            strip_headers=False,
        )
        sub_splitter = SemanticChunker(
            embeddings=FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5"),
        )

        docs = []
        for document in self.documents:
            size = len(document.page_content.split(" "))
            if should_ignore(document):
                continue
            elif size > sub_split_threshold:
                documents = main_splitter.split_text(document.page_content)
                temp_documents = []
                for temp_document in documents:
                    if len(temp_document.page_content.split(" ")) < min_size_threshold:
                        continue
                    elif (
                        len(temp_document.page_content.split(" ")) > sub_split_threshold
                    ):
                        ds = sub_splitter.split_text(temp_document.page_content)
                        for d in ds:
                            if len(d.split(" ")) >= min_size_threshold:
                                temp_documents.append(
                                    WebsiteDocument(
                                        page_content=d,
                                        document_meta=document.document_meta,
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

    def save_faq_documents(
        self, filepath: PathLike, jsonl: Optional[bool] = False
    ) -> None:
        """save the faqs to the given filepath"""
        content = [doc.to_json() for doc in self.faqs]
        with open(filepath, "w") as file:
            if jsonl:
                for c in content:
                    file.write(json.dumps(c) + "\n")
            else:
                json.dump(content, file)
