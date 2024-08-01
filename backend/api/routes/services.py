from typing import Any

import requests
import yfinance
from langchain_core.messages import HumanMessage, AIMessage
from backend.core.finance_agents_network.agent_network import AgentsNetwork
from backend.core.finance_agents_network.agents.personal_finance_agent import (
    PersonalFinanceAgent,
)
from backend.core.finance_agents_network.agents.market_analyzer_agent import (
    MarketAnalyzerAgent,
)
from backend.core.finance_agents_network.agents.investor_agent import InvestorAgent
from backend.core.finance_agents_network.prompts import (
    market_analyzer_prompt,
    investor_prompt,
    personal_finance_prompt,
)

url_map = {
    "groww-mutual-fund-search": "https://groww.in/v1/api/search/v3/query/global/st_p_query?entity_type=scheme&page=0&query={query}&size=10&web=true",
    "groww-mutual-fund-details": "https://groww.in/v1/api/data/mf/web/v3/scheme/search/{id}",
}


def get_groww_mutual_fund(fund_name: str) -> dict[str, Any]:
    search_url = url_map["groww-mutual-fund-search"]
    details_url = url_map["groww-mutual-fund-details"]
    try:
        q = requests.get(search_url.format(query="Baroda BNP Paribas Large Cap Fund"))
        r = requests.get(details_url.format(id=q.json()["data"]["content"][0]["id"]))
    except Exception as e:
        return {
            "status": "error",
            "message": "Something went wrong. Please try again later.",
        }

    return {"status": "success", "data": r.json()}


def get_stock_details(stock_ticker: str) -> dict[str, Any]:
    try:
        stock = yfinance.Ticker(stock_ticker)
        info = stock.info
        return {
            "oneYearChange": info["52WeekChange"],
            "symbol": stock_ticker,
            "currentPrice": info["regularMarketPreviousClose"],
            "companyName": info["longName"],
        }
    except:
        return {
            "message": "Something went wrong. Please try again later.",
        }


def stream_graph(messages: list):
    agent_network = AgentsNetwork()
    agent_network.add_agent(
        "MarketAnalyzerAgent", MarketAnalyzerAgent, market_analyzer_prompt
    )
    agent_network.add_agent("InvestorAgent", InvestorAgent, investor_prompt)
    agent_network.add_agent(
        "PersonalFinanceAgent", PersonalFinanceAgent, personal_finance_prompt
    )

    chat_messages = []
    for message in messages:
        if message["sender"] == "user":
            chat_messages.append(HumanMessage(message["text"]))
        else:
            chat_messages.append(AIMessage(message["text"]))

    graph = agent_network.create_agent_network()
    return graph.stream({"messages": chat_messages}, {"recursion_limit": 20})
