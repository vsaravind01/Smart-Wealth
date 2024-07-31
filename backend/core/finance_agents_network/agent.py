import os
from typing import Optional

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI

OPENAI_CHAT_MODEL_DEPLOYMENT = os.environ["OPENAI_CHAT_MODEL_DEPLOYMENT"]
OPENAI_API_VERSION = os.environ["OPENAI_API_VERSION"]


class Agent:
    def __init__(
        self,
        name: str,
        tools: Optional[list],
        system_prompt: str,
    ) -> None:
        self.name = name
        self.tools = tools if tools else []
        self.system_prompt = system_prompt

        self.llm = AzureChatOpenAI(
            azure_deployment=OPENAI_CHAT_MODEL_DEPLOYMENT,
            api_version=OPENAI_API_VERSION,
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

    def create_agent(self) -> str:
        """Create a function-calling agent and add it to the graph."""
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK, another assistant with different tools "
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any of the other assistants have the final answer or deliverable,"
                    " prefix your response with FINAL ANSWER so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}",
                ),
                MessagesPlaceholder(variable_name="messages"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        prompt = prompt.partial(system_message=self.system_prompt)
        prompt = prompt.partial(
            tool_names=", ".join([tool.name for tool in self.tools])
        )
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        executor = AgentExecutor(agent=agent, tools=self.tools)
        return executor
