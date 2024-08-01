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
            " MarketAnalyzerAgent: Responsible for fetching news, expert advice and market metrics related to a company."
            " InvestorAgent: Responsible for allocating the users principal amount into Equity, Mutual Funds and Gold."
            " PersonalFinanceAgent: Responsible for providing with appropriate loan and insurance options. You should always"
            " ask PersonalFinanceAgent if the user is above 25 years old or he is buying a vehicle or a house."
            " END the conversation when all the workers have finished their tasks. Do not give any worker the same task twice."
            " Whenever the user asks for a financial advice, you should pass the conversation to InvestorAgent."
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
