import os
from enum import Enum
import json
from collections import defaultdict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI

from backend.core.finance_agents_network.agent import Agent
from backend.document_loader.nse_document_loader import NseIndexLoader
from backend.vector_stores.azure_cosmos_db import AzureCosmosVectorStore

OPENAI_CHAT_MODEL_DEPLOYMENT = os.environ["OPENAI_CHAT_MODEL_DEPLOYMENT"]
OPENAI_API_VERSION = os.environ["OPENAI_API_VERSION"]


class InvestmentPeriod(Enum):
    SHORT_TERM = "short-term"
    MID_TERM = "mid-term"
    LONG_TERM = "long-term"


class RiskAppetite(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class InvestorAgent(Agent):
    funds = {
        InvestmentPeriod.SHORT_TERM: {
            RiskAppetite.LOW: "debt mutual fund",
            RiskAppetite.MODERATE: "liquid fund",
            RiskAppetite.HIGH: "hybrid fund",
        },
        InvestmentPeriod.MID_TERM: {
            RiskAppetite.LOW: "balanced large-cap mutual fund",
            RiskAppetite.MODERATE: "balanced large-cap mutual fund",
            RiskAppetite.HIGH: "multi-cap mutual funds",
        },
        InvestmentPeriod.LONG_TERM: {
            RiskAppetite.LOW: "large-cap mutual funds",
            RiskAppetite.MODERATE: "mid-cap mutual funds",
            RiskAppetite.HIGH: "small-cap mutual funds",
        },
    }

    stock_news_attributes = [
        "Acquisition",
        "New product launches",
        "New partnerships or collaborations",
        "Financial results",
    ]
    expert_news_attributes = [
        "Financials", ""
    ]
    stock_news_vector_store = AzureCosmosVectorStore(
        database_name="smart-wealth-main-db", container_name="stock-news"
    )
    expert_news_vector_store = AzureCosmosVectorStore(
        database_name="smart-wealth-main-db", container_name="expert-news"
    )

    def __init__(self, name: str, system_prompt: str) -> None:
        tools = [
            self.calculate_asset_allocation,
            self.allocate_mutual_funds,
            self.allocate_stocks,
        ]
        super().__init__(name, tools, system_prompt)

    @staticmethod
    def get_search_queries(company: str, search_attributes: list) -> list:
        return [
            f"Documents having news related to {attribute} of {company}"
            for attribute in search_attributes
        ]

    @staticmethod
    def get_company_analysis(company_list: list) -> list:
        """
        Get news summaries and expert analysis for the provided list of companies.
        """
        combined_analysis = defaultdict(
            lambda: {
                "sector": set(),
                "news_summary": set(),
                "segments": set(),
                "analysis_summary": set(),
            }
        )

        for company in company_list:
            company_name = company["company"]
            print(f"Processing analysis for company: {company_name}")

            # Get news summaries
            search_queries_news = InvestorAgent.get_search_queries(
                company_name, InvestorAgent.stock_news_attributes
            )
            for query in search_queries_news:
                print("News query----->>", query)
                search_results_news = (
                    InvestorAgent.stock_news_vector_store.vector_search(
                        query, top_k=3, threshold=0.3, with_embeddings=False
                    )
                )
                for res in search_results_news:
                    combined_analysis[company_name]["sector"].update(
                        res.document.document_meta.sector
                    )
                    combined_analysis[company_name]["news_summary"].add(
                        res.document.document_meta.summary
                    )

            # Get expert analysis
            search_queries_expert = InvestorAgent.get_search_queries(
                company_name, InvestorAgent.expert_news_attributes
            )
            for query in search_queries_expert:
                print("Expert Analysis query----->>", query)
                search_results_expert = (
                    InvestorAgent.expert_news_vector_store.vector_search(
                        query, top_k=3, threshold=0.3, with_embeddings=False
                    )
                )
                for res in search_results_expert:
                    combined_analysis[company_name]["segments"].update(
                        res.document.document_meta.segments
                    )
                    combined_analysis[company_name]["analysis_summary"].add(
                        res.document.document_meta.summary
                    )

        result = [
            {
                "company_name": company,
                "rank": details.get("rank", None),
                "ticker": details.get("ticker", None),
                "growth": details.get("growth", None),
                "sector": list(details["sector"]),
                "news_summary": list(details["news_summary"]),
                "segments": list(details["segments"]),
                "analysis_summary": list(details["analysis_summary"]),
            }
            for company, details in combined_analysis.items()
        ]
        return result

    @staticmethod
    @tool("asset_allocation", return_direct=False)
    def calculate_asset_allocation(age: int) -> dict:
        """
        Allocates portions of users principal amount into Equity, Mutual Funds and Gold.
        """
        rounded_age = ((age + 9) // 10) * 10
        equity = 100 - rounded_age
        mutual_funds = 0.65 * rounded_age
        gold = rounded_age - mutual_funds

        print(
            "Asset Allocation: ",
            {"equity": equity, "mutual_funds": mutual_funds, "gold": gold},
        )
        return {"equity": equity, "mutual_funds": mutual_funds, "gold": gold}

    @staticmethod
    @tool("allocate_mutual_funds", return_direct=False)
    def allocate_mutual_funds(top_companies: list) -> dict:
        """
        Provides guidance on how to allocate a portion of the portfolio across various equity funds.
        """
        top_companies_ticker = []
        nse_loader = NseIndexLoader()

        for company in top_companies:
            company_name = company.get("company")
            if company_name:
                ticker = nse_loader.get_ticker_from_company_name(company_name)
                if ticker:
                    top_companies_ticker.append(ticker)

        print("Mutual Funds Allocation", top_companies_ticker)
        investment_period = InvestmentPeriod.LONG_TERM
        risk_appetite = RiskAppetite.MODERATE

        if isinstance(investment_period, InvestmentPeriod) and isinstance(
            risk_appetite, RiskAppetite
        ):
            fund_type = InvestorAgent.funds[investment_period][risk_appetite]
            mutual_fund_vector_store = AzureCosmosVectorStore(
                database_name="smart-wealth-main-db", container_name="mutual-fund"
            )
            filter = {
                "document_meta.scheme_riskometer": {"ilike": risk_appetite.value},
                "document_meta.tickers": {"in": top_companies_ticker},
            }
            response = mutual_fund_vector_store.filter_documents(filters=filter)

            fund_json_list = []
            for document in response:
                meta = document.document_meta
                fund_json_list.append(
                    {
                        "fund_name": meta.fund_name,
                        "investment_objective": meta.investment_objective,
                        "tickers": meta.tickers,
                        "scheme_riskometer": meta.scheme_riskometer,
                        "portfolio": meta.portfolio,
                        "minimum_investment_amount": meta.minimum_investment_amount,
                    }
                )
            return json.dumps(fund_json_list[:5], indent=4)

    @staticmethod
    @tool("allocate_stocks", return_direct=False)
    def allocate_stocks(age, risk_tolerance, investment_period, top_companies) -> dict:
        """
        Allocates the investment balance among selected stocks based on their expected returns and user Account balance
        """
        print(
            "Stock allocation: ", age, risk_tolerance, investment_period, top_companies
        )
        personal_details = {
            "age": age,
            "risk_tolerance": risk_tolerance,
            "investment_period": investment_period,
        }
        top_companies_summary = InvestorAgent.get_company_analysis(top_companies)

        prompt = f"""You are a financial advisor, and you have a list of well-performing companies filtered by a clustering algorithm. Each company comes with relevant financial news such as acquisitions, new product launches, new partnerships or collaborations, and financial results. Additionally, important financial ratios and data for each company are provided.
        You also have personal details of an investor, including their bank account balance, age, the risk they are willing to take, and whether they prefer short-term, mid-term, or long-term investing.
        Based on this information, recommend the best stocks to buy along with the quantities to achieve maximum returns for the investor.

        Investor Details:
        {personal_details}

        Task:
        Analyze the provided information.
        Recommend the best stocks to buy.
        Specify the quantities of each stock to achieve maximum returns, considering the investor's risk profile and investment horizon.

        Typescript:
        {{
        'company_name':Name of the company choose to invest,
        'quantity': number of stocks decided to buy,
        'reason':Reason for choosing the stocks
        }}

        Note:
        -Ensure the total investment amount does not exceed the investor's bank account balance.
        -Align the stock picks with the investor's medium risk tolerance and mid-term investment horizon.
        -Do not describe anything return only json.

        """
        llm_instance = AzureChatOpenAI(
            azure_deployment=OPENAI_CHAT_MODEL_DEPLOYMENT,
            api_version=OPENAI_API_VERSION,
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=str(top_companies_summary)),
        ]
        response = llm_instance.invoke(messages)
        print("res", response)
        return response.content
