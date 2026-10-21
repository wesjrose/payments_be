from fastapi import APIRouter, HTTPException

from app.database import SessionDep

from app.payments.models import CheckoutSnapshot
from app.payments.service import get_payment_service

import uuid

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
def get_checkout_snapshot(session: SessionDep):
    new_checkout_snap = CheckoutSnapshot(
        total=cart["amount"],
        subtotal=cart["subtotal"],
        data=cart["data"],
        currency=cart["currency"],
        tax=cart["tax"],
    )
    session.add(new_checkout_snap)
    session.commit()
    session.refresh(new_checkout_snap)
    return new_checkout_snap


@router.get("/initiate-payment/{checkout_snapshot_id}")
def initiate_payment(checkout_snapshot_id: uuid.UUID, session: SessionDep):
    """
    This endpoint is simulating creating a payment intent for a
    user based on their checkout snapshot
    """

    print(f"The ID is: {checkout_snapshot_id}")
    snapshot = session.get(CheckoutSnapshot, checkout_snapshot_id)

    if snapshot is None:
        raise HTTPException(status_code=404, detail="Checkout snapshot not found")

    payment_service = get_payment_service(session)
    client_secret = payment_service.initiate_payment(snapshot)

    return client_secret
