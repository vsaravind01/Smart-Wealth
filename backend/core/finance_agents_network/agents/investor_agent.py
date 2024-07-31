import os
from enum import Enum
import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI

from backend.core.finance_agents_network.agent import Agent
from backend.vector_stores.azure_cosmos_db import AzureCosmosVectorStore

OPENAI_CHAT_MODEL_DEPLOYMENT = os.environ["OPENAI_CHAT_MODEL_DEPLOYMENT"]
OPENAI_API_VERSION = os.environ["OPENAI_API_VERSION"]


class InvestmentPeriod(Enum):
    SHORT_TERM = "short-term"
    MID_TERM = "mid-term"
    LONG_TERM = "long-term"


class RiskAppetite(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class InvestorAgent(Agent):
    funds = {
        InvestmentPeriod.SHORT_TERM: {
            RiskAppetite.LOW: "debt mutual fund",
            RiskAppetite.MEDIUM: "liquid fund",
            RiskAppetite.HIGH: "hybrid fund",
        },
        InvestmentPeriod.MID_TERM: {
            RiskAppetite.LOW: "balanced large-cap mutual fund",
            RiskAppetite.MEDIUM: "balanced large-cap mutual fund",
            RiskAppetite.HIGH: "multi-cap mutual funds",
        },
        InvestmentPeriod.LONG_TERM: {
            RiskAppetite.LOW: "large-cap mutual funds",
            RiskAppetite.MEDIUM: "mid-cap mutual funds",
            RiskAppetite.HIGH: "small-cap mutual funds",
        },
    }

    def __init__(self, name: str, system_prompt: str) -> None:
        tools = [
            self.calculate_asset_allocation,
            self.allocate_mutual_funds,
            self.allocate_stocks,
        ]
        super().__init__(name, tools, system_prompt)

    @staticmethod
    @tool("asset_allocation", return_direct=False)
    def calculate_asset_allocation(age: int) -> dict:
        """
        Allocates portions of users principal amount into Equity, Mutual Funds and Gold.
        """
        rounded_age = ((age + 9) // 10) * 10
        equity = 100 - rounded_age
        mutual_funds = 0.65 * equity
        gold = equity - mutual_funds

        return {"equity": equity, "mutual_funds": mutual_funds, "gold": gold}

    @staticmethod
    @tool("allocate_mutual_funds", return_direct=False)
    def allocate_mutual_funds(mutual_fund_split,suggested_companies,desired_sector) -> dict:
        """
        Provides guidance on how to allocate a portion of the portfolio across various equity funds.
        """
        investment_period = InvestmentPeriod.LONG_TERM
        risk_appetite = RiskAppetite.MEDIUM
        if isinstance(investment_period, InvestmentPeriod) and isinstance(
            risk_appetite, RiskAppetite
        ):
            fund_type = InvestorAgent.funds[investment_period][risk_appetite]
            mutual_fund_vector_store = AzureCosmosVectorStore(
                database_name="smart-wealth-main-db", container_name="mutual-fund"
            )
            # response = mutual_fund_vector_store.filter_documents(
            #     filters={
            #         "document_meta.minimum_investment_amount": {
            #             "lt": mutual_fund_split
            #         },
            #         "document_meta.scheme_riskometer": {"like": fund_type},
            #         "document_meta.tickers": {"in": ["suggested_companies"]},
            #         "document_meta.sectoral_composition": {"in": ["desired_sector"]},
            #     }
            # )
            filter = {
                "AND": {
                    "document_meta.sectoral_composition_list": desired_sector,
                    "document_meta.scheme_riskometer": {
                        "ilike":fund_type
                    },
                    "document_meta.tickers":suggested_companies
                }
            }
            response=mutual_fund_vector_store.filter_documents(filters=filter)

            fund_json_list = []
            for document in response:
                meta = document.document_meta
                fund_json_list.append(
                    {
                        "fund_name": meta.fund_name,
                        "investment_objective": meta.investment_objective,
                        "scheme_riskometer": meta.scheme_riskometer,
                        "portfolio": meta.portfolio.v2,
                        "minimum_investment_amount": meta.minimum_investment_amount,
                    }
                )
            return json.dumps(fund_json_list[:5], indent=4)

    @staticmethod
    @tool("allocate_stocks", return_direct=False)
    def allocate_stocks(suggested_companies: list) -> dict:
        """
        Provides guidance on how to allocate a portion of the portfolio across various mutual funds.
        """
        personal_details = {
            "age": 20,
            "risk_tolerance": "medium",
            "investment_period": 20,
        }
        """
        Allocates the investment balance among selected stocks based on their expected returns and user Account balance
        """

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
            HumanMessage(content=str(suggested_companies)),
        ]
        response = llm_instance.invoke(messages)
        return response.content
