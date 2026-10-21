from fastapi import APIRouter

from app.database import SessionDep

from app.payments.models import CheckoutSnapshot
from app.payments.service import get_payment_service

router = APIRouter(prefix="/payments", tags=["payments"])

cart = {
    "amount": 10025,
    "data": {
        "items": [{"id": "item_1", "amount": 10000}, {"id": "item_2", "amount": 25}]
    },
    "currency": "cad",
}


@router.get("/initiate-payment")
def initiate_payment(session: SessionDep):
    """
    This endpoint is simulating creating a payment intent for a
    user based on their checkout snapshot
    """

    # creating a new checkout snapshot
    new_checkout_snap = CheckoutSnapshot(
        amount=cart["amount"], data=cart["data"], currency=cart["currency"]
    )
    session.add(new_checkout_snap)
    session.commit()
    session.refresh(new_checkout_snap)

    # handling payments
    payment_service = get_payment_service(session)
    payment_service.initiate_payment(new_checkout_snap)

    return new_checkout_snap
