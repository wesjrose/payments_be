from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

load_dotenv()  # must run before configure_logging() so LOG_* settings apply

from app.logging_config import configure_logging, request_logging_middleware

configure_logging()

from app.database import engine
from app.payments.router import router as payments_router

from sqlmodel import SQLModel

from contextlib import asynccontextmanager

import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="Payment Example API", version="0.1.0", lifespan=lifespan)

cors_origins = [
    origin.strip().rstrip("/") for origin in os.getenv("CORS_ORIGINS", "").split(",")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(request_logging_middleware)

app.include_router(payments_router)


@app.get("/health")
def health() -> dict[str, str]:

    return {"status": "ok"}


# @app.post("/example")
# def example(data: Message) -> dict:

#     return {
#         "received": data.model_dump(),
#         "reply": f"Hello {data.name}, you said: {data.message}",
#     }
