from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import mutual_fund, stock, agent


app = FastAPI()

main_router = APIRouter(prefix="/api")
main_router.include_router(mutual_fund.router)
main_router.include_router(stock.router)
main_router.include_router(agent.router)

app.include_router(main_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*", "GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health-check")
def health_check():
    return {"status": "ok"}
