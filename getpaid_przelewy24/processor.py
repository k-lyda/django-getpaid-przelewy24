import json
import logging
from urllib.parse import urljoin

from django import http
from django.db.transaction import atomic
from django.http import HttpResponse
from django.urls import reverse
from django_fsm import can_proceed
from getpaid.exceptions import LockFailure
from getpaid.processor import BaseProcessor
from getpaid.types import BackendMethod as bm

# from getpaid_przelewy24.models import Payment
from getpaid_przelewy24.client import Client
from getpaid_przelewy24.types import Currency, BuyerData

logger = logging.getLogger(__name__)


class PaymentProcessor(BaseProcessor):
    display_name = "Przelewy24"
    accepted_currencies = [c.value for c in Currency]
    ok_statuses = [200, 201, 302]
    logo_url = None
    slug = "przelewy24"
    sandbox_url = "https://sandbox.przelewy24.pl/"
    production_url = "https://secure.przelewy24.pl/"
    method = "REST"
    confirmation_method = "PUSH"  #: PUSH - paywall will send POST request to your server; PULL - you need to check the payment status
    client_class = Client

    #
    # def __init__(self, payment: Payment):
    #     super().__init__(payment)
    #     self.payment = payment

    def get_client_params(self) -> dict:
        return {
            "api_url": self.get_paywall_baseurl(),
            "pos_id": self.get_setting("pos_id"),
            "secret_id": self.get_setting("secret_id"),
            "crc": self.get_setting("crc"),
        }

    # Helper methods
    def get_paywall_context(self, request=None, camelize_keys=False, **kwargs):
        """
        :param request: request creating the payment
        :return: dict that unpacked will be accepted by :meth:`Client.new_order`
        """
        loc = "127.0.0.1"
        our_baseurl = self.get_our_baseurl(request)
        url_return = urljoin(
            our_baseurl, reverse("getpaid:callback", kwargs={"pk": self.payment.pk})
        )
        context = {
            "session_id": self.payment.get_unique_id(),
            "amount": self.payment.amount_required,
            "currency": self.payment.currency,
            "buyer": BuyerData(email=self.payment.order.get_buyer_info()["email"]),
            "url_return": url_return,
            "description": self.payment.description,
            "time_limit": self.payment.time_limit,
            "channel": self.payment.channel,
            "wait_for_result": self.payment.wait_for_result,
        }
        if self.get_setting("confirmation_method", self.confirmation_method) == "PUSH":
            context["url_status"] = urljoin(
                our_baseurl, reverse("getpaid:callback", kwargs={"pk": self.payment.pk})
            )
        return context

    def get_paywall_method(self):
        return self.get_setting("paywall_method", self.method)

    # Communication with paywall
    @atomic()
    def prepare_transaction(self, request=None, view=None, **kwargs) -> HttpResponse:
        method = self.get_paywall_method().upper()
        if method == bm.REST:
            try:
                results = self.prepare_lock(request=request, **kwargs)
                response = http.HttpResponseRedirect(results["url"])
            except LockFailure as exc:
                logger.error(exc, extra=getattr(exc, "context", None))
                self.payment.fail()
                response = http.HttpResponseRedirect(
                    reverse("getpaid:payment-failure", kwargs={"pk": self.payment.pk})
                )
            self.payment.save()
            return response

    def prepare_lock(self, request=None, **kwargs):
        results = {}
        params = self.get_paywall_context(request=request, **kwargs)
        response = self.client.register_transaction(**params)
        results["raw_response"] = self.client.last_response
        self.payment.confirm_prepared()
        self.payment.token = results["token"] = response.get("data", {}).get("token")
        results["url"] = self.client.get_transaction_url(self.payment.token)
        return results

    def handle_paywall_callback(self, request, **kwargs):
        body = request.body.decode()
        data = json.loads(body)

        signature_params = {key: data[key] for key in data if key != 'sign'}
        expected_signature = self.client.get_sign(signature_params)
        signature = data.get("sign")
        if expected_signature == signature:
            self.payment.external_id = data.get("orderId")
            if can_proceed(self.payment.confirm_payment):
                self.payment.confirm_payment()
                if can_proceed(self.payment.mark_as_paid):
                    self.payment.mark_as_paid()
            else:
                logger.debug(
                    "Cannot confirm payment",
                    extra={
                        "payment_id": self.payment.id,
                        "payment_status": self.payment.status,
                    },
                )
            self.payment.save()
            return HttpResponse("OK")
        else:
            logger.error(
                f"Received bad signature for payment {self.payment.id}! "
                f"Got '{signature}', expected '{expected_signature}'"
            )
            return HttpResponse(
                "BAD SIGNATURE", status=422
            )  # https://httpstatuses.com/422
