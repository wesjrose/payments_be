from stripe import StripeClient

from app.payments.models import CheckoutSnapshot, PaymentIntentStatus, PaymentIntent
from app.payments.payment_service import PaymentHandler
from app.database import SessionDep
from app.helpers import get_or_create

from functools import lru_cache
import os


@lru_cache
def get_stripe_client() -> StripeClient:
    return StripeClient(os.getenv("STRIPE_API_KEY"))


class StripeService(PaymentHandler):

    def __init__(self, stripe_client: StripeClient, session: SessionDep):
        self.stripe_client = stripe_client
        self.session = session

    def initiate_payment(self, checkout_snapshot: CheckoutSnapshot):
        """
        This method initiates the payment. The checkout snapshot represents
        the items/purchases that the user wants to make when they checkout.
        """
        pi = self.stripe_client.v1.payment_intents.create(
            {
                "amount": checkout_snapshot.total,
                "currency": checkout_snapshot.currency,
            },
            {"idempotency_key": str(checkout_snapshot.id)},
        )

        # creating the payment intent
        local_pi = PaymentIntent(
            payment_intent_id=pi.id,
            amount=checkout_snapshot.total,
            currency=checkout_snapshot.currency,
            checkout_snapshot_id=checkout_snapshot.id,
            status=PaymentIntentStatus.CREATED,
        )
        local_pi, _ = get_or_create(
            self.session,
            PaymentIntent,
            defaults={
                "payment_indent_id": pi.id,
                "amount": checkout_snapshot.total,
                "currency": checkout_snapshot.currency,
                "status": PaymentIntentStatus.CREATED,
            },
            checkout_snapshot_id=checkout_snapshot.id,
        )

        self.session.add(local_pi)
        self.session.commit()

        return pi.client_secret
