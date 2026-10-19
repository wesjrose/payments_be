from fastapi import FastAPI
from fastapi import Depends, FastAPI, HTTPException, Query

from app.routers import items
from app.schemas import Message
from app.models import CheckoutSnapshot
from app.database import SessionDep, engine

from sqlmodel import Field, Session, SQLModel, create_engine, select

from contextlib import asynccontextmanager
from typing import Any
import uuid, os


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="Payment Example API", version="0.1.0", lifespan=lifespan)

app.include_router(items.router)


# example data used
cart = {
    "amount": 10025,
    "data": {
        "items": [{"id": "item_1", "amount": 10000}, {"id": "item_2", "amount": 25}]
    },
}


@app.get("/health")
def health() -> dict[str, str]:

    return {"status": "ok"}


@app.get("/create-payment-intent")
def create_payment_intent(session: SessionDep):
    """
    This endpoint is simulating creating a payment intent for a
    user based on their checkout snapshot
    """

    # creating a new checkout snapshot
    new_checkout_snap = CheckoutSnapshot(amount=cart["amount"], data=cart["data"])
    session.add(new_checkout_snap)
    session.commit()
    session.refresh(new_checkout_snap)

    return new_checkout_snap


@app.post("/example")
def example(data: Message) -> dict:

    return {
        "received": data.model_dump(),
        "reply": f"Hello {data.name}, you said: {data.message}",
    }
