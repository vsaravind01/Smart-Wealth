from __future__ import annotations

import json
from io import StringIO
from os import PathLike
from typing import Optional

from backend.models.documents import BaseDocument
from backend.models.documents.tags import tag_map


class BaseDataLoader:
    """Base DataLoader class"""

    @staticmethod
    def set_tags(
        documents: list[BaseDocument],
        must_tags: Optional[list[str]] = None,
    ):
        """set tags of the document in place"""
        if not must_tags:
            must_tags = []
        for document in documents:
            _tags = set()
            if must_tags:
                _tags = set(must_tags)
            for key, tags in tag_map.items():
                for tag in tags:
                    if (
                        tag in document.document_meta.source
                        or tag in document.document_meta.description
                        or tag in document.document_meta.title
                    ):
                        _tags.add(tag)
            document.document_meta.tags = list(_tags)

    @staticmethod
    def save_dataset(content: str | StringIO, filepath: PathLike):
        """save the dataset to the given filepath"""
        with open(filepath, "w") as file:
            json.dump(content, file)
