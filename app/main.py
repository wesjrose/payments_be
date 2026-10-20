from fastapi import FastAPI
from fastapi import FastAPI

from app.schemas import Message
from app.database import engine
from app.payments.router import router as payments_router

from sqlmodel import SQLModel

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="Payment Example API", version="0.1.0", lifespan=lifespan)

app.include_router(payments_router)


@app.get("/health")
def health() -> dict[str, str]:

    return {"status": "ok"}


@app.post("/example")
def example(data: Message) -> dict:

    return {
        "received": data.model_dump(),
        "reply": f"Hello {data.name}, you said: {data.message}",
    }
