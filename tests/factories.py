import factory
import swapper
from paywall.models import PaymentEntry

from getpaid_przelewy24.types import Currency


class OrderFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("color_name")
    total = factory.Faker(
        "pydecimal", positive=True, right_digits=2, min_value=10, max_value=500
    )
    currency = Currency.PLN

    class Meta:
        model = swapper.load_model("getpaid", "Order")


class PaymentFactory(factory.django.DjangoModelFactory):
    order = factory.SubFactory(OrderFactory)
    amount_required = factory.SelfAttribute("order.total")
    currency = factory.SelfAttribute("order.currency")
    description = factory.SelfAttribute("order.name")
    backend = "getpaid_przelewy24"
    url_return = "https://example.com/return"
    time_limit = 15
    channel = 1
    wait_for_result = True
    token = None

    class Meta:
        model = swapper.load_model("getpaid", "Payment")


class PaywallEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PaymentEntry
