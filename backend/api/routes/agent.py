from typing import Any

from fastapi import APIRouter

from backend.api.routes.services import stream_graph
from langchain_core.messages import AIMessage

router = APIRouter(prefix="/agent")


@router.post("/chat")
async def chat(messages: dict[str, Any]):
    """
    Chat with the agent network.
    """
    response = []
    messages = messages["messages"]

    for r in stream_graph(messages):
        for key, value in r.items():
            print("\n\n")
            print("-----------------")
            if "messages" in value:
                for m in value["messages"]:
                    if isinstance(m, AIMessage):
                        print(m.content)
                        response.append({"sender": "bot", "text": m.content})

    final_response = {
        "messages": [*messages, *response],
    }
    return final_response
