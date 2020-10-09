import pytest

from getpaid_przelewy24.client import Client
from getpaid_przelewy24.types import Currency, BuyerData

pytestmark = pytest.mark.django_db


@pytest.fixture(scope="session")
def p24_client():
    yield Client(
        api_url="https://sandbox.przelewy24.pl",
        pos_id=123252,
        secret_id="09f4976bac3f63f3698a6b463a0ac2a7",
        crc="3c76241ef55498ae"
    )

# @pytest.mark.skip(reson="Only for manual testing with sandbox")
def test_register_transaction_on_sandbox(p24_client):
    session_id = f"testowa_sesja_123_121"
    buyer = BuyerData(email="konrad.lyda@gmail.com", lastName="Lyda", firstName="Konrad")

    result = p24_client.register_transaction(
        session_id=session_id,
        amount=1.11,
        currency=Currency.PLN,
        buyer=buyer,
        url_return="https://example.com"
    )
    assert "data" in result
    assert "responseCode" in result
    assert "token" in result["data"]


# @pytest.mark.skip(reson="Only for manual testing with sandbox")
def test_get_transation_info_from_sandbox(p24_client):
    session_id = f"testowa_sesja_123_12"

    result = p24_client.get_transaction_info(session_id)
    assert "data" in result
    assert "responseCode" in result
    assert "sessionId" in result["data"]


@pytest.mark.skip(reson="Only for manual testing with sandbox")
def test_verify_transaction(p24_client):
    session_id = "testowa_sesja_123_12"
    order_id = 305849920

    result = p24_client.verify_transaction(
        session_id=session_id,
        amount=1.11,
        currency=Currency.PLN,
        order_id=order_id
    )
    assert "data" in result
    assert "responseCode" in result
    assert "status" in result["data"]