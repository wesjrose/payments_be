from app.helpers import utcnow

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON, DateTime, func

from datetime import datetime
from typing import Any, Optional
import uuid


class CheckoutSnapshot(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    subtotal: int
    total: int
    tax: int
    data: dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    payment_intent: Optional["PaymentIntent"] = Relationship(
        back_populates="checkout_snapshot", sa_relationship_kwargs={"uselist": False}
    )
    currency: str
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now(), "onupdate": utcnow},
    )


class PaymentIntent(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    payment_intent_id: str = Field(max_length=100)
    amount: int
    currency: str
    checkout_snapshot_id: uuid.UUID = Field(
        foreign_key="checkoutsnapshot.id", unique=True, ondelete="CASCADE"
    )
    checkout_snapshot: CheckoutSnapshot = Relationship(back_populates="payment_intent")
