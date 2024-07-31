from langchain_core.tools import tool

from backend.core.finance_agents_network.agent import Agent
from backend.models.documents.website_document import WebsiteDocument
from backend.vector_stores.bob_web_db import BobWebVectorStore


class PersonalFinanceAgent(Agent):
    vector_store = BobWebVectorStore(
        database_name="smart-wealth-main-db", container_name="bob-web"
    )

    def __init__(self, name: str, system_prompt: str) -> None:
        tools = [self.search_loan_documents, self.search_insurance_documents]
        super().__init__(name, tools, system_prompt)

    @staticmethod
    @tool("search_loan_documents", return_direct=False)
    def search_loan_documents(query: str) -> list[dict[str, str]]:
        """
        Get loan documents related to the provided query.
        """
        loan_documents = PersonalFinanceAgent.vector_store.vector_search(
            query,
            top_k=3,
            threshold=0.3,
            with_embeddings=False,
            doc_type="loan",
        )
        results = []
        for doc in loan_documents:
            assert isinstance(doc.document, WebsiteDocument)
            results.append(
                {
                    "page_title": doc.document.document_meta.title,
                    "page_description": doc.document.document_meta.description,
                    "page_content": doc.document.page_content,
                }
            )

        return results

    @staticmethod
    @tool("search_insurance_documents", return_direct=False)
    def search_insurance_documents(query: str) -> list[dict[str, str]]:
        """
        Get insurance documents related to the provided query.
        """
        insurance_documents = PersonalFinanceAgent.vector_store.vector_search(
            query,
            top_k=3,
            threshold=0.3,
            with_embeddings=False,
            doc_type="insurance",
        )
        results = []
        for doc in insurance_documents:
            assert isinstance(doc.document, WebsiteDocument)
            results.append(
                {
                    "page_title": doc.document.document_meta.title,
                    "page_description": doc.document.document_meta.description,
                    "page_content": doc.document.page_content,
                }
            )

        return results
