import os
from collections import defaultdict

from langchain_core.tools import tool

from backend.core.finance_agents_network.agent import Agent
from backend.vector_stores.azure_cosmos_db import AzureCosmosVectorStore


class MarketAnalyzerAgent(Agent):
    stock_news_attributes = [
        "Acquisition",
        "New product launches",
        "New partnerships or collaborations",
        "Financial results",
    ]
    expert_news_attributes = [
        "Acquisition",
        "New product launches",
        "New partnerships or collaborations",
        "Financial results",
    ]
    stock_news_vector_store = AzureCosmosVectorStore(
        database_name="smart-wealth-main-db", container_name="stock-news"
    )
    expert_news_vector_store = AzureCosmosVectorStore(
        database_name="smart-wealth-main-db", container_name="expert-news"
    )

    def __init__(self, name: str, system_prompt: str) -> None:
        tools = [
            self.get_news_articles,
            self.get_expert_analysis,
        ]
        super().__init__(name, tools, system_prompt)

    @staticmethod
    def get_search_queries(company: str, search_attributes: list) -> list:
        return [
            f"Documents having news related to {attribute} of {company}"
            for attribute in search_attributes
        ]

    @staticmethod
    @tool("get_news_articles", return_direct=False)
    def get_news_articles(company_list: list) -> list:
        """
        Get news summaries for the provided list of companies.
        """
        news_articles = defaultdict(lambda: {"sector": set(), "news_summary": set()})
        for company in company_list:
            search_queries = MarketAnalyzerAgent.get_search_queries(
                company, MarketAnalyzerAgent.stock_news_attributes
            )
            for query in search_queries:
                search_results = (
                    MarketAnalyzerAgent.stock_news_vector_store.vector_search(
                        query, top_k=3, threshold=0.3, with_embeddings=False
                    )
                )
                for res in search_results:
                    news_articles[company]["sector"].update(
                        res.document.document_meta.sector
                    )
                    news_articles[company]["news_summary"].add(
                        res.document.document_meta.summary
                    )

        return [
            {
                "company_name": company,
                "sector": list(news["sector"]),
                "news_summary": list(news["news_summary"]),
            }
            for company, news in news_articles.items()
        ]

    @staticmethod
    @tool("get_expert_analysis", return_direct=False)
    def get_expert_analysis(company_list: list) -> list:
        """
        Get expert analysis for the provided list of companies.
        """
        expert_analysis = defaultdict(
            lambda: {"segments": set(), "analysis_summary": set()}
        )
        for company in company_list:
            search_queries = MarketAnalyzerAgent.get_search_queries(
                company, MarketAnalyzerAgent.expert_news_attributes
            )
            for query in search_queries:
                search_results = (
                    MarketAnalyzerAgent.expert_news_vector_store.vector_search(
                        query, top_k=3, threshold=0.3, with_embeddings=False
                    )
                )
                for res in search_results:
                    expert_analysis[company]["segments"].update(
                        res.document.document_meta.segments
                    )
                    expert_analysis[company]["analysis_summary"].add(
                        res.document.document_meta.summary
                    )

        return [
            {
                "company_name": company,
                "segments": list(news["segments"]),
                "analysis_summary": list(news["analysis_summary"]),
            }
            for company, news in expert_analysis.items()
        ]
