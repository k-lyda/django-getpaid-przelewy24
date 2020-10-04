import uuid
from decimal import Decimal

import pytest
from django.urls import reverse_lazy
from getpaid.exceptions import (
    LockFailure,
    ChargeFailure
)
from pytest import raises

from getpaid_przelewy24.types import Currency, BuyerData

pytestmark = pytest.mark.django_db

url_api_operate = reverse_lazy("paywall:api_operate")


@pytest.mark.parametrize(
    "before,after",
    [
        ({"price": 100}, {"price": Decimal("1")}),
        ({"amount": 100}, {"amount": Decimal("1")}),
        ([{"amount": 100}], [{"amount": Decimal("1")}]),
        ({"internal": {"amount": 100}}, {"internal": {"amount": Decimal("1")}}),
        ({"internal": [{"amount": 100}]}, {"internal": [{"amount": Decimal("1")}]}),
        (
            [{"internal": [{"amount": 100}]},],
            [{"internal": [{"amount": Decimal("1")}]},],
        ),
    ],
)
def test_normalize(before, after, getpaid_client):
    result = getpaid_client._normalize_convertibles(before)
    assert result == after


@pytest.mark.parametrize(
    "before,after",
    [
        ({"price": 1}, {"price": 100}),
        ({"amount": 1}, {"amount": 100}),
        ({"price": 1.0}, {"price": 100}),
        ({"price": Decimal("1")}, {"price": 100}),
        ([{"price": Decimal("1")}], [{"price": 100}]),
        ({"internal": {"price": Decimal("1")}}, {"internal": {"price": 100}}),
        (
            {"internal": [{"price": Decimal("1")}]},
            {"internal": [{"price": 100}]},
        ),
        (
            [{"internal": [{"price": Decimal("1")}]}],
            [{"internal": [{"price": 100}]}],
        ),
    ],
)
def test_centify(before, after, getpaid_client):
    result = getpaid_client._centify_convertibles(before)
    assert result == after

@pytest.mark.parametrize(
    "params,sign",
    [
        ({
             "sessionId": "test_123",
             "merchantId": 123456,
             "amount": 123,
             "currency": "PLN",
             "crc": "3f76241ef53498a1test"
         }, "336f3cefc5478b040d638890f22cc9e48b77bff5e880db0bb2f1d06b71918424256457d4ccf996c2ed296cb30e01e88f"),
        ({"sessionId": "testowa_sesja_123_12", "orderId": 111222333, "amount": 111, "currency": "PLN",
          "crc": "3f76241ef53498a1test"},
         "8e2c83d756106937b69954b49e63683d496202bfa2a80da8b676477d1d49b317c0db2c11ee9257fec4aaaa26d9114f30")
    ],
)
def test_sign_calculation(params, sign, getpaid_client):
    result = getpaid_client._get_sign(params)
    assert result == sign


def test_register_transaction(getpaid_client, requests_mock):
    session_id = f"{uuid.uuid4()}"
    buyer = BuyerData(email="buyer@example.com")
    requests_mock.post(
        "/api/v1/transaction/register",
        json={
          "data": {
            "token": "1A2B3C4D5E-A1B2C3-A1B2C3-1A2B3C4D5E"
          },
          "responseCode": "0"
        },
        status_code=200,
    )

    result = getpaid_client.register_transaction(
        session_id=session_id,
        amount=1.23,
        currency=Currency.PLN,
        buyer=buyer,
    )
    assert "data" in result
    assert "responseCode" in result
    assert "token" in result["data"]


@pytest.mark.parametrize("response_status", [400, 401, 403, 500, 501])
def test_register_transaction_failure(response_status, getpaid_client, requests_mock):
    session_id = f"{uuid.uuid4()}"
    buyer = BuyerData(email="buyer@example.com")
    requests_mock.post(
        "/api/v1/transaction/register", text="FAILURE", status_code=response_status,
    )
    with raises(LockFailure):
        getpaid_client.register_transaction(
            session_id=session_id,
            amount=1.23,
            currency=Currency.PLN,
            buyer=buyer,
        )


def test_verify_transaction(getpaid_client, requests_mock):
    session_id = f"{uuid.uuid4()}"
    order_id = "300147701"
    requests_mock.put(
        "/api/v1/transaction/verify",
        json={
          "data": {
            "status": "success"
          },
          "responseCode": "0"
        },
        status_code=200,
    )

    result = getpaid_client.verify_transaction(
        session_id=session_id,
        amount=1.23,
        currency=Currency.PLN,
        order_id=order_id
    )
    assert "data" in result
    assert "responseCode" in result
    assert "status" in result["data"]


@pytest.mark.parametrize("response_status", [400, 401, 403, 500, 501])
def test_verify_transaction_failure(response_status, getpaid_client, requests_mock):
    session_id = f"{uuid.uuid4()}"
    order_id = "300147701"
    requests_mock.put(
        "/api/v1/transaction/verify",
        text="FAILURE",
        status_code=response_status,
    )
    with raises(ChargeFailure):
        getpaid_client.verify_transaction(
            session_id=session_id,
            amount=1.23,
            currency=Currency.PLN,
            order_id=order_id
        )


def test_get_transation_info(getpaid_client, requests_mock):
    session_id = f"{uuid.uuid4()}"
    requests_mock.get(
        f"/api/v1/transaction/by/sessionId/{session_id}",
        json={
            "data": {
                "statement": "string",
                "orderId": 0,
                "sessionId": f"{session_id}",
                "status": 0,
                "amount": 123,
                "currency": "PLN",
                "date": "201701010000",
                "dateOfTransaction": "201701010000",
                "clientEmail": "example@przelewy24.pl",
                "accountMD5": "string",
                "paymentMethod": 0,
                "description": "string",
                "clientName": "string",
                "clientAddress": "string",
                "clientCity": "string",
                "clientPostcode": "string",
                "batchId": 0,
                "fee": "0"
            },
            "responseCode": "0"
            },
        status_code=200,
    )

    result = getpaid_client.get_transaction_info(
        session_id=session_id,
    )
    assert "data" in result
    assert "responseCode" in result
    assert "sessionId" in result["data"]
    assert result["data"]["sessionId"] == session_id
    assert result["data"]["amount"] == Decimal('1.23')

    assert result["data"]["sessionId"] == session_id
