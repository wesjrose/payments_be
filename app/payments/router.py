from fastapi import APIRouter, HTTPException, Request

from app.database import SessionDep

from app.payments.models import CheckoutSnapshot
from app.payments.service import get_payment_service
from app.helpers import get_or_create
from app.logging_config import get_logger

import uuid

logger = get_logger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])

cart = {
    "amount": 11328,
    "subtotal": 10025,
    "data": {
        "items": [{"id": "item_1", "amount": 10000}, {"id": "item_2", "amount": 25}]
    },
    "currency": "cad",
    "tax": 13.03,
}


@router.get("/checkout-info")
def get_checkout_info(session: SessionDep):

    checkout_info = {
        "amount": cart["amount"],
        "tax": cart["tax"],
        "currency": cart["currency"],
    }

    return checkout_info


@router.post("/checkout-snapshot")
def create_checkout_snapshot(session: SessionDep, request: Request):

    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        raise HTTPException(
            status_code=400, detail="Idempotency-Key header is required"
        )

    snapshot, created = get_or_create(
        session,
        CheckoutSnapshot,
        idempotency_key=idempotency_key,
        defaults={
            "total": cart["amount"],
            "subtotal": cart["subtotal"],
            "data": cart["data"],
            "currency": cart["currency"],
            "tax": cart["tax"],
        },
    )

    return snapshot


@router.get("/initiate-payment/{checkout_snapshot_id}")
def initiate_payment(checkout_snapshot_id: uuid.UUID, session: SessionDep):
    """
    This endpoint is simulating creating a payment intent for a
    user based on their checkout snapshot
    """

    logger.info(
        "Initiating payment",
        extra={"checkout_snapshot_id": str(checkout_snapshot_id)},
    )
    snapshot = session.get(CheckoutSnapshot, checkout_snapshot_id)

    if snapshot is None:
        logger.warning(
            "Checkout snapshot not found",
            extra={"checkout_snapshot_id": str(checkout_snapshot_id)},
        )
        raise HTTPException(status_code=404, detail="Checkout snapshot not found")

    payment_service = get_payment_service(session)
    client_secret = payment_service.initiate_payment(snapshot)

    return client_secret


@router.post("/webhooks")
async def handle_webhooks(session: SessionDep, request: Request):

    payload = await request.body()
    headers = dict(request.headers)

    payment_service = get_payment_service(session)
    payment_service.ingest_webhook_messages(payload, headers)

    return {"message": "hello world"}
