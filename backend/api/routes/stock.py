from backend.api.routes import services
from fastapi import APIRouter

router = APIRouter(prefix="/stocks")


@router.get("/")
async def get_stocks_info(stocks: str) -> dict:
    stocks = stocks.split(",")
    stock_details = []
    for stock in stocks:
        stock_details.append(services.get_stock_details(stock))
    return {"status": "success", "data": stock_details}


@router.get("/{stock_ticker}")
async def get_stock_info(stock_ticker: str) -> dict:
    stock_detail = services.get_stock_details(stock_ticker)
    return {"status": "success", "data": stock_detail}
