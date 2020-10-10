import pytest

from getpaid_przelewy24.client import Client
from getpaid_przelewy24.types import Currency, BuyerData

pytestmark = pytest.mark.django_db


@pytest.fixture(scope="session")
def p24_client():
    yield Client(
        api_url="https://sandbox.przelewy24.pl",
        pos_id=123252,
        secret_id="09f5416bac3f63f3698a6b463a0ac2a7",
        crc="31c6223ea55498ae_test"
    )

@pytest.mark.skip(reson="Only for manual testing with sandbox")
def test_register_transaction_on_sandbox(p24_client):
    session_id = f"rejestracja_1231_error"
    buyer = BuyerData(email="konrad.lyda@gmail.com", lastName="Lyda", firstName="Konrad")

    result = p24_client.register_transaction(
        session_id=session_id,
        amount=1.11,
        currency=Currency.PLN,
        buyer=buyer,
        url_return="https://example.com/payment-done",
        url_status="https://example.com/payment-callback"
    )
    assert "data" in result
    assert "responseCode" in result
    assert "token" in result["data"]
    print(p24_client.get_transaction_url(result["data"]["token"]))


@pytest.mark.skip(reson="Only for manual testing with sandbox")
def test_get_transation_info_from_sandbox(p24_client):
    session_id = f"rejestracja_1231_error"

    result = p24_client.get_transaction_info(session_id)
    assert "data" in result
    assert "responseCode" in result
    assert "sessionId" in result["data"]
    print(result)


@pytest.mark.skip(reson="Only for manual testing with sandbox")
def test_verify_transaction(p24_client):
    session_id = "rejestracja_1231_ok"
    order_id = 305857109

    result = p24_client.verify_transaction(
        session_id=session_id,
        amount=1.11,
        currency=Currency.PLN,
        order_id=order_id
    )
    assert "data" in result
    assert "responseCode" in result
    assert "status" in result["data"]
    print(result)
