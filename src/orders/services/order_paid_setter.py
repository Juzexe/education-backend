from dataclasses import dataclass

from django.utils import timezone

from banking.selector import get_bank
from orders.models import Order


@dataclass
class OrderPaidSetter:
    """Mark order as paid"""

    order: Order
    silent: bool | None = False

    def __post_init__(self) -> None:
        """Save order state at boot time"""
        self.is_already_paid = self.order.paid is not None
        self.is_already_shipped = self.order.shipped is not None

    def __call__(self) -> None:
        self.mark_order_as_paid()
        self.call_bank_successfull_callback()
        self.ship()

    def mark_order_as_paid(self) -> None:
        self.order.paid = timezone.now()
        if not self.is_already_paid:  # reset unpayment date if order is not paid yet
            self.order.unpaid = None

        self.order.save()

    def ship(self) -> None:
        if not self.is_already_shipped and not self.is_already_paid and self.order.item is not None:
            self.order.ship(silent=self.silent)

    def call_bank_successfull_callback(self) -> None:
        Bank = get_bank(self.order.bank_id)
        bank = Bank(order=self.order)
        bank.successful_payment_callback()
