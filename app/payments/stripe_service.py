from stripe import StripeClient

from app.payments.models import CheckoutSnapshot
from app.payments.payment_service import PaymentHandler
from app.database import SessionDep

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
            {"amount": checkout_snapshot.total, "currency": checkout_snapshot.currency}
        )
        print(f"The payment intent generated is: {pi}")
        return pi.client_secret
