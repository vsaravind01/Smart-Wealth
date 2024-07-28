import os
from typing import Any, Literal, Optional, Sequence

from backend.models.documents import BaseDocument, EmbeddingDocument
from backend.vector_stores.azure_cosmos_db import AzureCosmosVectorStore
from backend.models.loader_utils.type_maps import SourceMap


class BobWebVectorStore(AzureCosmosVectorStore):
    """Bob Web Vector Store"""

    def __init__(
        self,
        database_name: Optional[str] = None,
        container_name: Optional[str] = None,
        *args,
        **kwargs,
    ):
        if not database_name:
            database_name = os.environ["BOB_AZURE_COSMOS_DATABASE_NAME"]
        if not container_name:
            container_name = os.environ["BOB_AZURE_COSMOS_WEB_CONTAINER_NAME"]

        super().__init__(
            database_name=database_name, container_name=container_name, *args, **kwargs
        )

    def vector_search(
        self,
        query: str,
        top_k: int = 10,
        doc_type: str = None,
        threshold: Optional[float] = 0.0,
        with_embeddings: Optional[bool] = False,
        filters: Optional[dict[Literal["AND", "OR"], Any]] = None,
    ) -> list[EmbeddingDocument]:

        assert doc_type is not None, "kind must be provided"
        assert doc_type in SourceMap, f"kind must be one of {SourceMap}"

        if filters is None:
            filters = {}

        filters["document_meta.source_map"] = doc_type

        return super().vector_search(
            query=query,
            top_k=top_k,
            threshold=threshold,
            with_embeddings=with_embeddings,
            filters=filters,
        )

    def filter_documents(
        self,
        filters: dict[str, Any],
        kind: Optional[str] = None,
        columns: Sequence[str] = None,
    ) -> list[BaseDocument]:
        assert kind is not None, "kind must be provided"
        assert kind in SourceMap, f"kind must be one of {SourceMap}"
        if kind:
            filters["document_meta.source_map"] = kind

        return super().filter_documents(filters=filters, columns=columns)
