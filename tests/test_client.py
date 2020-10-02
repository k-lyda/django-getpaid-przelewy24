import uuid
from decimal import Decimal

import pytest
from django.urls import reverse_lazy
from getpaid.exceptions import (
    LockFailure,
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


@pytest.mark.parametrize("response_status", [200, 201, 302])
def test_transaction_registration(response_status, getpaid_client, requests_mock):
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
        status_code=response_status,
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
def test_transaction_registration_failure(response_status, getpaid_client, requests_mock):
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
