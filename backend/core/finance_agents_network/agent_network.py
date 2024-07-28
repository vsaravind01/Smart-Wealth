import os
import operator
from typing import Annotated, Sequence, TypedDict, Dict, List
import functools

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langchain_openai import AzureChatOpenAI
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser


from backend.core.finance_agents_network.agents.market_analyzer_agent import (
    MarketAnalyzerAgent,
)

OPENAI_CHAT_MODEL_DEPLOYMENT = os.environ["OPENAI_CHAT_MODEL_DEPLOYMENT"]
OPENAI_API_VERSION = os.environ["OPENAI_API_VERSION"]


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
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
        return {"messages": [HumanMessage(content=result["output"], name=name)]}

    def create_chain(self, prompt, function_def: dict):
        agent_chain = (
            prompt
            | self.llm.bind_functions(functions=[function_def], function_call="route")
            | JsonOutputFunctionsParser()
        )
        return agent_chain

    def create_agent_network(self) -> None:
        self.graph = StateGraph(AgentState)

        for agent_name, agent_instance in self.agents.items():
            agent = agent_instance.create_agent()
            node = functools.partial(self.agent_node, agent=agent, name=agent_name)
            self.graph.add_node(agent_name, node)

        principal_agent_name = "PrincipalAgent"
        options = ["FINISH"] + list(self.agents.keys())
        function_def = {
            "name": "route",
            "description": "Select the next role.",
            "parameters": {
                "title": "routeSchema",
                "type": "object",
                "properties": {
                    "next": {
                        "title": "Next",
                        "anyOf": [{"enum": options}],
                    }
                },
                "required": ["next"],
            },
        }
        principal_system_prompt = (
            "You are a supervisor tasked with managing a conversation between the"
            " following workers: {members}. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH."
        ).format(members=", ".join(self.agents.keys()))

        principal_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", principal_system_prompt),
                MessagesPlaceholder(variable_name="messages"),
                (
                    "system",
                    "Given the conversation above, who should act next?"
                    " Or should we FINISH? Select one of: {options}",
                ),
            ]
        ).partial(options=str(options), members=", ".join(self.agents.keys()))

        supervisor_chain = self.create_chain(principal_prompt, function_def)
        self.graph.add_node(principal_agent_name, supervisor_chain)

        for agent_name in self.agents:
            self.graph.add_edge(agent_name, principal_agent_name)

        conditional_map = {k: k for k in self.agents.keys()}
        conditional_map["FINISH"] = END
        self.graph.add_conditional_edges(
            principal_agent_name, lambda x: x["next"], conditional_map
        )

        self.graph.set_entry_point(principal_agent_name)
        agent_network = self.graph.compile()

        return agent_network


network = AgentsNetwork()
network.add_agent("MarketAnalyzerAgent", MarketAnalyzerAgent, "Market Analyzer Prompt")
graph = network.create_agent_network()

config = {"recursion_limit": 20}
for s in graph.stream(
    {"messages": [HumanMessage(content="Get the news of Infosys Limited")]},
    config=config,
):
    if "__end__" not in s:
        print(s)
        print("----")
