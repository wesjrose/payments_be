from abc import ABC, abstractmethod

from app.payments.models import CheckoutSnapshot


class PaymentHandler(ABC):
    name: str

    @abstractmethod
    def initiate_payment(self, checkout_snapshot: CheckoutSnapshot):
        """Initiates that payment based on the amount in the checkout snapshot"""
