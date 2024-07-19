from __future__ import annotations

import json
from io import StringIO
from os import PathLike
from typing import Optional

from backend.models.documents import BaseDocument
from backend.models.documents.tags import tag_map


class BaseDataLoader:
    """Base DataLoader class"""

    def __init__(self, tag_set: Optional[list[str]] = None):
        self.tag_set: set[str] = set(tag_set) if tag_set else set()
        self.documents: list[BaseDocument] = []

    def iter_from_attrs(self, attrs: list[str] | str):
        """Get all values from the documents given the attributes.
        The sub attributes can be provided as a list and the attributes
        will be inferred in order.

        Args:
        ------
        attrs: list[str] | str
            if type(attrs) is list then the attributes will be inferred in order.
            If type(attrs) is str then only the top level attribute will be inferred.

        Yields:
        -------
        document: BaseDocument
            The value of the attribute of the documents
        """
        assert len(attrs), "Attributes (attrs) cannot be empty"

        if isinstance(attrs, str):
            attrs = [attrs]
        for document in self.documents:
            _doc = document
            for attr in attrs:
                _doc = getattr(_doc, attr)
            yield _doc

    @staticmethod
    def set_tags(
        documents: list[BaseDocument],
        tag_fields: list[str] = None,
        must_tags: Optional[list[str]] = None,
    ):
        """set tags of the document in place"""
        if not must_tags:
            must_tags = []
        if not tag_fields:
            tag_fields = ["source"]
        for document in documents:
            _tags = set()
            if must_tags:
                _tags = set(must_tags)
            for key, tags in tag_map.items():
                for tag in tags:
                    if any(tag in getattr(document, field) for field in tag_fields):
                        _tags.add(tag)
            document.document_meta.tags = list(_tags)

    @staticmethod
    def save_dataset(content: str | StringIO, filepath: PathLike):
        """save the dataset to the given filepath"""
        with open(filepath, "w") as file:
            json.dump(content, file)
