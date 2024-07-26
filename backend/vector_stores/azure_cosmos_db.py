from __future__ import annotations

import os
import time

import logging
from uuid import uuid4
from typing import Any, Callable, Generator, Optional

import tqdm
from openai.lib.azure import AzureOpenAI
from openai.types import CreateEmbeddingResponse
from azure.cosmos import CosmosClient, PartitionKey, ContainerProxy, DatabaseProxy

from backend.models.documents import BaseTextDocument, EmbeddingDocument
from backend.vector_stores.utils import num_tokens_from_string
from backend.vector_stores.config import container_to_document_map


logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_API_TYPE = os.environ["OPENAI_API_TYPE"]
OPENAI_API_VERSION = os.environ["OPENAI_API_VERSION"]
OPENAI_API_BASE = os.environ["OPENAI_API_BASE"]
OPENAI_EMBEDDINGS_MODEL_NAME = os.environ["OPENAI_EMBEDDINGS_MODEL_NAME"]
OPENAI_EMBEDDINGS_MODEL_DEPLOYMENT = os.environ["OPENAI_EMBEDDINGS_MODEL_DEPLOYMENT"]

AZURE_COSMOS_DB_HOST = os.environ["AZURE_COSMOS_DB_HOST"]
AZURE_COSMOS_DB_API_KEY = os.environ["AZURE_COSMOS_DB_API_KEY"]


class AzureCosmosVectorStore:
    vector_embedding_policy = {
        "vectorEmbeddings": [
            {
                "path": "/contextVector",
                "dataType": "float32",
                "distanceFunction": "cosine",
                "dimensions": 1536,
            }
        ]
    }

    indexing_policy = {
        "indexingMode": "consistent",
        "automatic": True,
        "includedPaths": [{"path": "/*"}],
        "vectorIndexes": [{"path": "/contextVector", "type": "quantizedFlat"}],
    }

    def __init__(
        self,
        database_name: str,
        container_name: str,
        is_vector_enabled: bool = True,
        partition_key: Optional[str] = "/document_meta/date_created",
    ):
        self.database_name = database_name
        self.container_name = container_name
        self.cosmos_client = CosmosClient(AZURE_COSMOS_DB_HOST, AZURE_COSMOS_DB_API_KEY)
        self.is_vector_enabled = is_vector_enabled
        self.cosmos_container_properties = {
            "partition_key": PartitionKey(path=partition_key)
        }
        self.cosmos_database_properties = {"id": database_name}
        self.azure_openai_client = AzureOpenAI(
            api_key=OPENAI_API_KEY,
            api_version=OPENAI_API_VERSION,
            azure_endpoint=OPENAI_API_BASE,
            azure_deployment=OPENAI_EMBEDDINGS_MODEL_DEPLOYMENT,
        )
        self.db: Optional[DatabaseProxy] = None
        self._container: Optional[ContainerProxy] = None

        self._embedding_key = self.vector_embedding_policy["vectorEmbeddings"][0][
            "path"
        ][1:]
        self._similarity_key = "SimilarityScore"

        self.__init_db()

    def __init_db(self):
        if self.db is None:
            self.db = self.cosmos_client.get_database_client(
                database=self.database_name
            )
        if self._container is None:
            if self.is_vector_enabled:
                self._container = self.db.create_container_if_not_exists(
                    id=self.container_name,
                    partition_key=self.cosmos_container_properties["partition_key"],
                    indexing_policy=self.indexing_policy,
                    vector_embedding_policy=self.vector_embedding_policy,
                )
            else:
                indexing_policy = self.indexing_policy
                indexing_policy.pop("vectorIndexes")
                self._container = self.db.create_container_if_not_exists(
                    id=self.container_name,
                    partition_key=self.cosmos_container_properties["partition_key"],
                    indexing_policy=indexing_policy,
                )
        logger.debug("Successfully initialized Azure Cosmos DB")

    def get_embeddings(
        self, text: str, model: Optional[str] = "text-embedding-ada-002"
    ):
        return self.azure_openai_client.embeddings.create(input=text, model=model)

    def upsert_documents(
        self,
        documents: list[BaseTextDocument],
        log_interval: Optional[int] = 100,
        document_range: Optional[tuple[int, int]] = (0, float("inf")),
    ) -> None:

        for idx, document in tqdm.tqdm(
            enumerate(documents), total=len(documents), desc="Uploading Documents"
        ):
            if document_range[0] <= idx < document_range[1]:
                if (idx + 1) % log_interval == 0:
                    logger.info(f"Successfully uploaded {idx + 1} of {len(documents)}")

                self.__upsert_document(document=document)

        logger.info("Successfully uploaded all documents")

    def embed_upsert_documents(
        self,
        documents: list[BaseTextDocument],
        template_iter: Callable[
            [list[BaseTextDocument]], Generator[tuple[str, BaseTextDocument]]
        ],
        model: Optional[str] = "text-embedding-ada-002",
        rate_limit: Optional[int] = 349000,
        max_token_limit: Optional[int] = float("inf"),
        log_interval: Optional[int] = 100,
        document_range: Optional[tuple[int, int]] = (0, float("inf")),
    ) -> int:
        """Embed and upload documents"""
        total_tokens = 0
        current_batch_tokens = 0

        for idx, (content, document) in tqdm.tqdm(
            enumerate(template_iter(documents)),
            total=len(documents),
            desc="Embedding & Uploading Documents",
        ):
            if document_range[0] <= idx < document_range[1]:
                if (idx + 1) % log_interval == 0:
                    logger.info(f"Successfully uploaded {idx + 1} of {len(documents)}")

                est_tokens = num_tokens_from_string(content, model)
                if est_tokens + current_batch_tokens > rate_limit:
                    time.sleep(60)
                    current_batch_tokens = 0

                response = self.azure_openai_client.embeddings.create(
                    input=content, model=model
                )
                total_tokens += response.usage.total_tokens
                current_batch_tokens += response.usage.total_tokens

                self.__upsert_document(embedding_response=response, document=document)

                if total_tokens > max_token_limit:
                    raise RuntimeError(
                        f"Max token limit exceeded. Max token limit is {max_token_limit}."
                        f" Current Usage is {total_tokens}."
                        f" Documents Uploaded : {idx + 1} of {len(documents)}."
                    )

        logger.info(
            f"Successfully uploaded all documents - Total Tokens Used : {total_tokens}"
        )
        return total_tokens

    def vector_search(
        self,
        query: str,
        top_k: int = 10,
        threshold: Optional[float] = 0.0,
        with_embeddings: bool = False,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[EmbeddingDocument]:
        embeddings = self.get_embeddings(query).data[0].embedding

        if filters:
            filter_string = " AND ".join(
                [f"c.{key} = '{value}'" for key, value in filters.items()]
            )
            filter_string = f"WHERE {filter_string}"
        else:
            filter_string = ""

        if with_embeddings:
            query = (
                "SELECT TOP {} c.id, c.page_content, c.document_meta, VectorDistance(c.{}, {}) AS "
                "{} FROM c {} ORDER BY VectorDistance(c.{}, {})".format(
                    top_k,
                    self._embedding_key,
                    embeddings,
                    self._similarity_key,
                    filter_string,
                    self._embedding_key,
                    embeddings,
                )
            )
        else:
            query = (
                "SELECT TOP {} c.id, c.page_content, c.document_meta, VectorDistance(c.{}, {}) AS "
                "{} FROM c {} ORDER BY VectorDistance(c.{}, {})".format(
                    top_k,
                    self._embedding_key,
                    embeddings,
                    self._similarity_key,
                    filter_string,
                    self._embedding_key,
                    embeddings,
                )
            )

        items = list(
            self._container.query_items(query=query, enable_cross_partition_query=True)
        )

        document_class = container_to_document_map[self.container_name]
        documents = []
        for item in items:
            if item[self._similarity_key] > threshold:
                document = EmbeddingDocument(
                    document=document_class(**item),
                    similarity_score=item[self._similarity_key],
                )
                if with_embeddings:
                    document.embedding = item[self._embedding_key]
                documents.append(document)
        return documents

    def __upsert_document(
        self,
        document: BaseTextDocument,
        embedding_response: Optional[CreateEmbeddingResponse] = None,
    ):
        document_dict = document.to_json()
        upload_dict = {
            "id": str(uuid4()),
            **document_dict,
        }
        if embedding_response:
            upload_dict[self._embedding_key] = embedding_response.data[0].embedding

        return self._container.upsert_item(upload_dict)
