from __future__ import annotations

import os
import time

import logging
from uuid import uuid4
from typing import Callable, Generator, Optional

from openai.lib.azure import AzureOpenAI
from openai.types import CreateEmbeddingResponse
from azure.cosmos import CosmosClient, PartitionKey

from backend.models.documents import BaseDocument, BaseTextDocument
from backend.vector_stores.utils import num_tokens_from_string


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
        "excludedPaths": [{"path": "/page_content"}],
        "vectorIndexes": [{"path": "/contextVector", "type": "quantizedFlat"}],
    }

    def __init__(
        self, database_name: str, container_name: str, partition_key="/date_created"
    ):
        self.database_name = database_name
        self.container_name = container_name
        self.cosmos_client = CosmosClient(AZURE_COSMOS_DB_HOST, AZURE_COSMOS_DB_API_KEY)
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
        self.db = None
        self.container = None

        self.__init_db()

    def __init_db(self):
        if self.db is None:
            self.db = self.cosmos_client.get_database_client(
                database=self.database_name
            )
            self.container = self.db.create_container_if_not_exists(
                id=self.container_name,
                partition_key=self.cosmos_container_properties["partition_key"],
                indexing_policy=self.indexing_policy,
                vector_embedding_policy=self.vector_embedding_policy,
            )

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

        for idx, (content, document) in enumerate(template_iter(documents)):
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
                total_tokens = response.usage.total_tokens
                current_batch_tokens += response.usage.total_tokens

                self.__upsert_document(embedding_response=response, document=document)

                if total_tokens > max_token_limit:
                    raise RuntimeError(
                        f"Max token limit exceeded. Max token limit is {max_token_limit}. Current Usage is {total_tokens}"
                    )

        logger.info(
            f"Successfully uploaded all documents - Total Tokens Used : {total_tokens}"
        )
        return total_tokens

    def __upsert_document(
        self, embedding_response: CreateEmbeddingResponse, document: BaseDocument
    ):
        document_dict = document.to_json()
        upload_dict = {
            "id": str(uuid4()),
            **document_dict,
            "contextVector": embedding_response.data[0].embedding,
        }

        return self.container.upsert_item(upload_dict)
