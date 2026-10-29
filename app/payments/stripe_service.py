from fastapi import Request, HTTPException

from app.payments.models import CheckoutSnapshot, PaymentIntentStatus, PaymentIntent
from app.payments.payment_service import PaymentHandler
from app.database import SessionDep
from app.helpers import get_or_create, get_sqs_client
from app.logging_config import get_logger

from functools import lru_cache
import os, json, stripe, boto3


@lru_cache
def get_stripe_client() -> stripe.StripeClient:
    return stripe.StripeClient(os.getenv("STRIPE_API_KEY"))


logger = get_logger(__name__)


class StripeService(PaymentHandler):

    def __init__(self, stripe_client: stripe.StripeClient, session: SessionDep):
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
                "payment_intent_id": str(pi.id),
            },
            checkout_snapshot_id=checkout_snapshot.id,
        )

        self.session.add(local_pi)
        self.session.commit()

        return pi.client_secret

    def _verify_webhook_message(self, payload: dict, headers: dict) -> stripe.Event:

        endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        sig_header = headers.get("stripe-signature")
        event = None
        try:
            event = self.stripe_client.construct_event(
                payload, sig_header, endpoint_secret
            )
        except stripe.error.SignatureVerificationError as e:
            logger.warning(
                "Stripe webhook signature failed authentication",
                extra=dict(headers.headers)
                | {"endpoint secret": endpoint_secret, "payload_type": type(payload)},
            )

            raise HTTPException(status_code=400, detail="Invalid request")

        return event

    def ingest_webhook_messages(self, payload: bytes, headers: dict):

        event = self._verify_webhook_message(payload, headers)

        sqs_client = get_sqs_client()
        sqs_client.send_message(
            QueueUrl=os.getenv("PAYMENT_MESSAGE_QUEUE"),
            MessageBody=str(
                {
                    "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
                    "receiptHandle": "MessageReceiptHandle-1",
                    "body": "Hello world from payments",
                    "attributes": {
                        "ApproximateReceiveCount": "1",
                        "SentTimestamp": "1523232000000",
                        "SenderId": "123456789012",
                        "ApproximateFirstReceiveTimestamp": "1523232000001",
                    },
                    "messageAttributes": {},
                    "md5OfBody": "7b270e59b47ff90a553787216d55d91d",
                    "eventSource": "aws:sqs",
                    "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:MyQueue",
                    "awsRegion": "us-east-1",
                },
            ),
            MessageAttributes={
                "event_type": {"DataType": "String", "StringValue": event.type},
                "event_id": {"DataType": "String", "StringValue": event.id},
            },
        )
        logger.warning(
            "Queued Stripe webhook",
            extra={"event_id": event.id, "event_type": event.type},
        )
