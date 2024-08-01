import os
from typing import Any

from fastapi import APIRouter
from backend.vector_stores import AzureCosmosVectorStore
from backend.api.routes import services

router = APIRouter(prefix="/mutual-funds")

mutual_fund_container = os.environ["BOB_AZURE_COSMOS_MF_CONTAINER_NAME"]


@router.get("/")
async def query_mutual_fund(funds: str) -> list[dict[str, Any]]:
    funds = funds.split(",")
    fund_details = []
    for fund in funds:
        fund_details.append(services.get_groww_mutual_fund(fund))
    return fund_details


@router.get("/{fund_name}")
async def get_mutual_fund(fund_name: str) -> dict:
    fund_detail = services.get_groww_mutual_fund(fund_name)
    return fund_detail
