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
        pos_id=123456,
        secret_id="09f49762ac3463f3698a6b463a1ac2a7",
        crc="3f76241ef53498a1test"
    )
