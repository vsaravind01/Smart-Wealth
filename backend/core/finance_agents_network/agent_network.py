import os
import operator
from typing import Annotated, Sequence, TypedDict
import functools
from pydantic import BaseModel
from contextlib import contextmanager
from typing import Literal

from langgraph.channels.context import Context
from langchain_core.messages import BaseMessage, AIMessage, ToolMessage
from langgraph.graph import END, StateGraph, START
from langchain_openai import AzureChatOpenAI
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langgraph.prebuilt import ToolNode

from backend.core.finance_agents_network.agents.principal_agent import PrincipalAgent

OPENAI_CHAT_MODEL_DEPLOYMENT = os.environ["OPENAI_CHAT_MODEL_DEPLOYMENT"]
OPENAI_API_VERSION = os.environ["OPENAI_API_VERSION"]


class AgentContext(BaseModel):
    age: int
    risk_tolerance: str
    investment_period: int
    market_data: list
    portfolio_allocation: dict


@contextmanager
def get_agent_context(config):
    try:
        yield AgentContext(
            age=20,
            risk_tolerance="medium",
            investment_period=20,
            market_data=[],
            portfolio_allocation={},
        )
    finally:
        pass


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    context: Annotated[AgentContext, Context(get_agent_context)]
    next: str


class AgentsNetwork:
    def __init__(self) -> None:
        self.agents = {}
        self.graph = None
        self.llm = AzureChatOpenAI(
            azure_deployment=OPENAI_CHAT_MODEL_DEPLOYMENT,
            api_version=OPENAI_API_VERSION,
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

    def add_agent(self, name: str, agent_class: type, system_prompt: str) -> None:
        agent_instance = agent_class(name, system_prompt)
        self.agents[name] = agent_instance

    def agent_node(self, state, agent, name):
        result = agent.invoke(state)
        if isinstance(result, ToolMessage):
            pass
        else:
            result = AIMessage(content=result["output"], name=name)
        return {
            "messages": [result],
            "next": name,
        }

    def create_chain(self, prompt, function_def: dict):
        agent_chain = (
            prompt
            | self.llm.bind_functions(functions=[function_def], function_call="route")
            | JsonOutputFunctionsParser()
        )
        return agent_chain

    @staticmethod
    def router(
        state,
    ) -> Literal["call_tool", "__end__", "continue", "MarketAnalyzerAgent"]:
        print("Router", state)
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "call_tool"
        if "FINAL ANSWER" in last_message.content:
            return "__end__"
        return "continue"

    def create_agent_network(self) -> None:
        self.graph = StateGraph(AgentState)

        self.tools = []
        for agent_name, agent_instance in self.agents.items():
            agent = agent_instance.create_agent()
            node = functools.partial(self.agent_node, agent=agent, name=agent_name)
            self.graph.add_node(agent_name, node)
            self.tools.extend(agent_instance.tools)
        tool_node = ToolNode(self.tools)
        self.graph.add_node("call_tool", tool_node)

        principal_agent = PrincipalAgent("PrincipalAgent", list(self.agents.keys()))
        supervisor_chain = self.create_chain(
            principal_agent.principal_chain_prompt, principal_agent.function_def
        )
        self.graph.add_node(principal_agent.name, supervisor_chain)

        self.graph.add_conditional_edges(
            "MarketAnalyzerAgent",
            self.router,
            {"continue": "PrincipalAgent", "call_tool": "call_tool", "__end__": END},
        )
        self.graph.add_conditional_edges(
            "InvestorAgent",
            self.router,
            {
                "continue": "PrincipalAgent",
                "call_tool": "call_tool",
                "__end__": END,
            },
        )
        self.graph.add_conditional_edges(
            "PersonalFinanceAgent",
            self.router,
            {"continue": "PrincipalAgent", "call_tool": "call_tool", "__end__": END},
        )
        self.graph.add_conditional_edges(
            "call_tool",
            lambda x: x["next"],
            {
                "MarketAnalyzerAgent": "MarketAnalyzerAgent",
                "InvestorAgent": "InvestorAgent",
                "PersonalFinanceAgent": "PersonalFinanceAgent",
            },
        )
        self.graph.add_edge(START, "PrincipalAgent")

        conditional_map = {k: k for k in self.agents.keys()}
        conditional_map["FINISH"] = END
        self.graph.add_conditional_edges(
            "PrincipalAgent", lambda x: x["next"], conditional_map
        )

        agent_network = self.graph.compile()
        return agent_network
