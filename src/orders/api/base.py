from typing import List, Optional

from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from django.http import HttpResponseRedirect

from app.pricing import format_price
from banking import price_calculator
from banking.selector import get_bank
from orders.api.validators import GiftValidator
from orders.api.validators import PurchaseValidator
from orders.models import Order
from orders.models import PromoCode
from orders.services.order_creator import OrderCreator
from users.models import User
from users.services import UserCreator


class PurchaseViewSet(ReadOnlyModelViewSet):
    """Abstract viewset for purchasable items"""

    @property
    def item(self):
        return self.get_object()

    @property
    def tags(self) -> list[str]:
        return [self.item.slug]

    @property
    def subscribe(self) -> bool:
        return str(self.request.POST.get("subscribe", False)).lower() in [
            "true",
            "1",
            "yes",
        ]

    @action(methods=["POST"], detail=True)
    def purchase(self, request, pk=None, **kwargs):
        """Direct order purchase"""
        data = request.POST

        PurchaseValidator.do(data, context={"request": self.request})

        order = self._create_order(data=data)
        payment_link = self.get_payment_link(order, data=data)

        return HttpResponseRedirect(redirect_to=payment_link)

    @action(methods=["POST"], detail=True)
    def gift(self, request, pk=None, **kwargs):
        """Purchase as a gift"""
        data = request.POST

        GiftValidator.do(data, context={"request": self.request})

        order = self._create_gift(data=data)
        payment_link = self.get_payment_link(order, data=data)

        return HttpResponseRedirect(redirect_to=payment_link)

    @action(methods=["GET"], detail=True)
    def promocode(self, request, pk=None, **kwargs):
        promocode = self._get_promocode(request)

        price = promocode.apply(self.item) if promocode is not None else self.item.price

        Bank = get_bank(desired=request.GET.get("desired_bank"))

        price = price_calculator.to_bank(Bank, price)

        return Response(
            {
                "price": price,
                "formatted_price": format_price(price),
                "currency": Bank.currency,
                "currency_symbol": Bank.currency_symbol,
            }
        )

    def _create_order(self, data) -> Order:
        creator = OrderCreator(
            user=self._create_user(
                name=data["name"],
                email=data["email"],
                subscribe=self.subscribe,
                tags=self.tags,
            ),
            item=self.item,
            promocode=data.get("promocode"),
            desired_bank=data.get("desired_bank"),
        )
        return creator()

    def _create_gift(self, data) -> Order:
        order_creator = OrderCreator(
            user=self._create_user(
                name=data["receiver_name"],
                email=data["receiver_email"],
                subscribe=self.subscribe,
                tags=[*self.tags, "gift_receiver"],
            ),
            giver=self._create_user(
                name=data["giver_name"],
                email=data["giver_email"],
                subscribe=self.subscribe,
                tags=[*self.tags, "gift_giver"],
            ),
            item=self.item,
            desired_shipment_date=data["desired_shipment_date"],
            gift_message=data.get("gift_message"),
            desired_bank=data.get("desired_bank"),
            promocode=data.get("promocode"),
        )

        return order_creator()

    def _create_user(self, name: str, email: str, subscribe: bool = False, tags: Optional[List[str]] = None) -> User:
        return UserCreator(
            name=name,
            email=email.strip(),
            subscribe=subscribe,
            tags=tags,
        )()

    def _get_promocode(self, request) -> Optional[PromoCode]:
        try:
            promocode_name = request.GET["promocode"]
        except KeyError:
            return None

        return PromoCode.objects.get_or_nothing(name=promocode_name)

    def get_payment_link(self, order: Order, data: dict):
        Bank = get_bank(desired=data.get("desired_bank"))
        bank = Bank(
            order=order,
            request=self.request,
            success_url=data.get("success_url"),
        )

        return bank.get_initial_payment_url()

    def list(self, request, *args, **kwargs):
        raise MethodNotAllowed("list")
