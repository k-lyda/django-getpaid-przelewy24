import pytest

from getpaid_przelewy24.client import Client


# from pytest_factoryboy import register
#
# from .factories import OrderFactory, PaymentFactory, PaywallEntryFactory
#
# register(PaymentFactory)
# register(OrderFactory)
# register(PaywallEntryFactory)


@pytest.fixture
def getpaid_client(requests_mock):
    yield Client(
        api_url="https://example.com/",
        pos_id=123251,
        secret_id="b6ca15b0d1020e8094d9b5f8d163db54",
        crc=300746,
    )
