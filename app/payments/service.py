from fastapi import Depends

from stripe import StripeClient

from app.database import SessionDep
from app.payments.stripe_service import StripePaymentHandler, get_stripe_client

from typing import Any, Annotated
import os


def get_payment_service(session: SessionDep):

    payment_provider = os.getenv("PAYMENT_PROVIDER", "stripe")

    if payment_provider == "stripe":
        return StripePaymentHandler(
            stripe_client=get_stripe_client(),
            session=session,
        )
