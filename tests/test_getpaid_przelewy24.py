import json
import uuid

import pytest
import swapper
from getpaid.types import BackendMethod as bm
from getpaid.types import ConfirmationMethod as cm
from getpaid.types import PaymentStatus as ps

pytestmark = pytest.mark.django_db

Order = swapper.load_model("getpaid", "Order")
Payment = swapper.load_model("getpaid", "Payment")

url_post_payment = "https://sandbox.przelewy24.pl/trnRequest/"
url_api_register = "https://sandbox.przelewy24.pl/api/v1/transaction/register"


def _prep_conf(api_method: bm = bm.REST, confirm_method: cm = cm.PUSH) -> dict:
    return {
        "getpaid_przelewy24": {
            "pos_id": 123252,
            "secret_id": "09f4976bac3f63f3698a6b463a0ac2a7",
            "crc": "3f76241ef53498a1test",
            "paywall_method": api_method,
            "confirmation_method": confirm_method,
        }
    }


@pytest.mark.parametrize("response_status", [200, 201, 302])
def test_rest_flow_begin(
    response_status, payment_factory, settings, requests_mock, getpaid_client
):
    token = f"{uuid.uuid4()}"
    requests_mock.post(
        "/api/v1/transaction/register",
        json={
            "data": {
                "token": f"{token}"
            },
            "responseCode": "0"
        },
        status_code=200,
    )

    settings.GETPAID_BACKEND_SETTINGS = _prep_conf(api_method=bm.REST)

    payment = payment_factory(external_id=uuid.uuid4())
    # requests_mock.post(str(url_api_register), json={"url": str(url_post_payment)})
    result = payment.prepare_transaction(None)

    assert result.status_code == 302
    assert payment.status == ps.PREPARED
    assert payment.token == token


# PUSH flow
def test_push_flow(
    payment_factory,
    settings,
    requests_mock,
    rf,
    getpaid_client,
):
    settings.GETPAID_BACKEND_SETTINGS = _prep_conf(confirm_method=cm.PUSH)

    payment = payment_factory(external_id=uuid.uuid4())
    payment.confirm_prepared()

    encoded = json.dumps(
        {
            "merchantId": getpaid_client.pos_id,
            "posId": getpaid_client.pos_id,
            "sessionId": payment.get_unique_id(),
            "amount": getpaid_client._centify(payment.amount_required),
            "originAmount": getpaid_client._centify(payment.amount_required),
            "currency": "PLN",
            "orderId": 12345678,
            "methodId": payment.channel,
            "statement": "string",
            "sign": getpaid_client.get_sign({
                "merchantId": getpaid_client.pos_id,
                "posId": getpaid_client.pos_id,
                "sessionId": payment.get_unique_id(),
                "amount": getpaid_client._centify(payment.amount_required),
                "originAmount": getpaid_client._centify(payment.amount_required),
                "currency": "PLN",
                "orderId": 12345678,
                "methodId": payment.channel,
                "statement": "string",
            })
        },
        default=str,
    )

    request = rf.post(
        "",
        content_type="application/json",
        data=encoded,
    )
    payment.handle_paywall_callback(request)
    assert payment.status == ps.PAID