from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from backend.core.finance_agents_network.agent import Agent


class PrincipalAgent(Agent):
    def __init__(self, name: str, options: list) -> None:
        self.tools = []
        self.options = ["FINISH"] + options
        self.members = ", ".join(options)

        self.system_prompt = (
            " You are a supervisor tasked with managing a conversation between the"
            " following workers: {members}. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH."
            " MarketAnalyzerAgent is responsible for fetching company related news, expert advice about a company and also fetches market metrics"
            " InvestorAgent is responsible for allocating the users pricipal amount into Equity, Mutual Funds and Gold."
        ).format(members=self.members)

        self.function_def = {
            "name": "route",
            "description": "Select the next role.",
            "parameters": {
                "title": "routeSchema",
                "type": "object",
                "properties": {
                    "next": {
                        "title": "Next",
                        "anyOf": [{"enum": self.options}],
                    }
                },
                "required": ["next"],
            },
        }

        self.principal_chain_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder(variable_name="messages"),
                (
                    "system",
                    "Given the conversation above, who should act next?"
                    " Or should we FINISH? Select one of: {options}",
                ),
            ]
        ).partial(options=str(self.options), members=self.members)

        super().__init__(name, self.tools, self.system_prompt)
