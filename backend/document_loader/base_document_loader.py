from __future__ import annotations

import json
from io import StringIO
from os import PathLike
from typing import Any, Iterable, Optional, Sequence, TypeVar, Generator, Generic

from backend.models.documents import BaseDocument, BaseTextDocument
from backend.vector_stores import AzureCosmosVectorStore

T = TypeVar("T", bound=BaseDocument)


class BaseDocumentLoader(Generic[T]):
    """Base DataLoader class"""

    def __init__(
        self,
        tag_set: Optional[list[str]] = None,
        tag_map: Optional[dict[str, list[str]]] = None,
    ):
        self.tag_set: set[str] = set(tag_set) if tag_set else set()
        self.tag_map: dict[str, list[str]] = tag_map if tag_map else {}
        self.documents: list[T] = []

    def split_documents(self, **kwargs) -> list[BaseDocument]:
        raise NotImplementedError()

    def iter_from_attrs(self, attrs: list[str] | str) -> Generator[Any]:
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
            _doc = self.get_document_attrs(document, attrs)
            yield _doc

    @staticmethod
    def get_document_attrs(document: BaseDocument, attrs: list[str]) -> str:
        _doc = document
        for attr in attrs:
            _doc = getattr(_doc, attr, None)
        return _doc

    def set_tags(
        self,
        documents: Iterable[BaseDocument],
        tag_fields: Sequence[list[str]] = None,
        must_tags: Optional[Iterable[str]] = None,
    ) -> None:
        """set tags of the document in place"""
        if not must_tags:
            must_tags = []
        if not tag_fields:
            tag_fields = [["document_meta", "source"]]
        for document in documents:
            _tags = set()
            if must_tags:
                _tags = set(must_tags)
            for key, tags in self.tag_map.items():
                for tag in tags:
                    values = [
                        self.get_document_attrs(document, tag_field)
                        for tag_field in tag_fields
                    ]
                    if any(tag in value for value in values if value):
                        _tags.add(key)
            document.document_meta.tags = list(_tags)

    def upsert_to_vector_store(
        self,
        database_name: str,
        container_name: str,
        log_interval: Optional[int] = 100,
        document_range: Optional[tuple[int, int]] = (0, float("inf")),
    ) -> None:
        vector_store = AzureCosmosVectorStore(
            database_name=database_name, container_name=container_name
        )
        documents_to_upload = self.documents

        vector_store.upsert_documents(
            documents_to_upload,
            log_interval=log_interval,
            document_range=document_range,
        )

    @staticmethod
    def iter_documents_from_template(
        documents: list[BaseTextDocument | BaseDocument],
    ) -> Generator[tuple[str, BaseTextDocument | BaseDocument]]:
        for document in documents:
            assert hasattr(
                document, "format_document"
            ), "The document must have a format_document method to be uploaded to the vector store"
            yield document.format_document(), document

    @classmethod
    def base_embed_upsert_to_vector_store(
        cls,
        documents: list[BaseDocument],
        database_name: str,
        container_name: str,
        max_token_limit: Optional[int] = float("inf"),
        document_range: Optional[tuple[int, int]] = (0, float("inf")),
    ) -> int:
        vector_store = AzureCosmosVectorStore(
            database_name=database_name, container_name=container_name
        )
        documents_to_upload = documents
        total_tokens = vector_store.embed_upsert_documents(
            documents=documents_to_upload,
            template_iter=cls.iter_documents_from_template,
            max_token_limit=max_token_limit,
            document_range=document_range,
        )
        return total_tokens

    @staticmethod
    def save_dataset(content: str | StringIO, filepath: PathLike) -> None:
        """save the dataset to the given filepath"""
        with open(filepath, "w") as file:
            json.dump(content, file)

    def save_documents(self, filepath: PathLike, jsonl: Optional[bool] = False) -> None:
        """save the documents to the given filepath"""
        content = [doc.to_json() for doc in self.documents]
        with open(filepath, "w") as file:
            if jsonl:
                for line in content:
                    file.write(json.dumps(line) + "\n")
            else:
                json.dump(content, file)

    def _load_documents(self, dataset: list[dict]) -> None:
        raise NotImplementedError()


class BaseTextDocumentLoader(BaseDocumentLoader[T]):
    def __init__(
        self,
        tag_set: Optional[list[str]] = None,
        tag_map: Optional[dict[str, list[str]]] = None,
        **kwargs,
    ):
        super().__init__(tag_set=tag_set, tag_map=tag_map)
        self.documents: list[T] = []

    def split_documents(self, **kwargs) -> list[BaseTextDocument]:
        raise NotImplementedError()

    def embed_upsert_to_vector_store(
        self,
        database_name: str,
        container_name: str,
        should_split: Optional[bool] = False,
        max_token_limit: Optional[int] = float("inf"),
        document_range: Optional[tuple[int, int]] = (0, float("inf")),
        split_document_kwargs: Optional[dict] = None,
    ) -> int:
        if not split_document_kwargs:
            split_document_kwargs = {}

        vector_store = AzureCosmosVectorStore(
            database_name=database_name, container_name=container_name
        )
        if should_split:
            documents_to_upload = self.split_documents(**split_document_kwargs)
        else:
            documents_to_upload = self.documents
        total_tokens = vector_store.embed_upsert_documents(
            documents=documents_to_upload,
            template_iter=self.iter_documents_from_template,
            max_token_limit=max_token_limit,
            document_range=document_range,
        )
        return total_tokens
