from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON

from typing import Any, Optional
import uuid


class CheckoutSnapshot(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    amount: int
    data: dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    payment_intent: Optional["PaymentIntent"] = Relationship(
        back_populates="checkout_snapshot", sa_relationship_kwargs={"uselist": False}
    )


class PaymentIntent(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    payment_intent_id: str = Field(max_length=100)
    checkout_snapshot_id: uuid.UUID = Field(
        foreign_key="checkoutsnapshot.id", unique=True, ondelete="CASCADE"
    )
    checkout_snapshot: CheckoutSnapshot = Relationship(back_populates="payment_intent")
