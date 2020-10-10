import json
from copy import deepcopy
from decimal import Decimal
from hashlib import sha384
from typing import Optional, Union
from urllib.parse import urljoin

import requests
from django.core.serializers.json import DjangoJSONEncoder
from getpaid.exceptions import (
    ChargeFailure
)
from getpaid.exceptions import (
    LockFailure, CommunicationError,
)
from getpaid.types import ItemInfo
from requests.auth import _basic_auth_str

from .types import (
    BuyerData,
    Currency,
    PaymentChannel,
    ChargeResponse, TransactionInfoResponse,

)


class Client:
    last_response = None
    _convertibles = {"amount", "price"}

    def __init__(
        self,
        api_url: str,
        pos_id: int,
        secret_id: str,
        crc: str,
        wait_for_result: bool = True
    ):
        self.api_url = api_url
        self.pos_id = pos_id
        self.secret_id = secret_id
        self.crc = crc
        self.wait_for_result = wait_for_result

    def _headers(self, **kwargs):
        auth_string = _basic_auth_str(self.pos_id, self.secret_id)
        data = {
            "Content-Type": "application/json",
            "Authorization": auth_string
        }
        data.update(kwargs)
        return data

    @classmethod
    def _centify(cls, v):
        return int(v * 100)

    @classmethod
    def _centify_convertibles(cls, data: Union[ItemInfo, dict, list, Decimal, int, float, str]):
        """
        Traverse through given object and convert all values of 'amount'
        fields and all keys to Przelewy24 format.
        :param data: Converted data
        """
        data = deepcopy(data)
        if hasattr(data, "items"):
            return {
                k: cls._centify(v) if k in cls._convertibles else cls._centify_convertibles(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [cls._centify_convertibles(v) for v in data]
        return data

    @classmethod
    def _normalize(cls, v: Union[Decimal, int, float]):
        return Decimal(v) / 100

    @classmethod
    def _normalize_convertibles(cls, data: Union[ItemInfo, dict, list, Decimal, int, float, str]):
        """
        Traverse through given object and convert all values of 'amount'
        fields to normal and all Przelewy24-specific keys to standard ones.
        :param data: Converted data
        """
        data = deepcopy(data)
        if hasattr(data, "items"):
            return {
                k: cls._normalize(v) if k in cls._convertibles else cls._normalize_convertibles(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [cls._normalize_convertibles(v) for v in data]
        return data

    def get_sign(self, params):
        params["crc"] = self.crc
        return sha384(json.dumps(params, separators=(',', ':')).encode('utf-8')).hexdigest()

    def get_transaction_url(self, token):
        return urljoin(self.api_url, f"/trnRequest/{token}")

    def register_transaction(
            self,
            session_id: str,
            amount: Union[Decimal, float],
            currency: Currency,
            buyer: BuyerData,
            url_return: str,
            description: Optional[str] = None,
            url_status: Optional[str] = None,
            time_limit: Optional[int] = None,
            channel: Optional[PaymentChannel] = None,
            wait_for_result: bool = True,
            **kwargs,
    ):
        """
            Register new transaction within API.

            :param session_id: Unique identifier from merchant's system
            :param amount: Payment amount
            :param currency: currency code
            :param description: Short description of the whole order
            :param url_return: URL address to which customer will be redirected when transaction is complete
            :param buyer: Buyer data (see :class:`Buyer`)
            :param url_status: URL address to which transaction status will be send
            :param time_limit: Time limit for transaction process, 0 - no limit, max. 99 (in minutes)
            :param channel: Channel Enum (see :class:`PaymentChannel`)
            :param wait_for_result: whether a user should wait for payment confirmation or be redirected back immediately after payment
            :param kwargs: Additional params that will first be consumed by headers, with leftovers passed on to order request
            :return: JSON response from API
        """
        url = urljoin(self.api_url, "/api/v1/transaction/register")
        data = self._centify_convertibles({
            "merchantId": self.pos_id,
            "posId": self.pos_id,
            "sessionId": session_id,
            "amount": amount,
            "currency": currency,
            "description": description if description else "Payment order",
            "email": buyer.email,
            "client": str(buyer),
            "country": "PL",
            "language": buyer.language if buyer.language else "pl",
            "urlReturn": url_return,
            "timeLimit": time_limit if time_limit else 0,
            "waitForResult": self.wait_for_result,
            "transferLabel": description if description else "Payment order",
            "sign": self.get_sign({
                "sessionId": session_id,
                "merchantId": self.pos_id,
                "amount": self._centify(amount),
                "currency": currency.value,
            }),
        })
        if url_status:
            data["urlStatus"] = url_status
        if channel:
            data["channel"] = channel
        headers = self._headers(**kwargs)
        data.update(kwargs)
        encoded = json.dumps(data, cls=DjangoJSONEncoder)
        self.last_response = requests.post(
            url, headers=headers, data=encoded, allow_redirects=False, auth=(self.pos_id, self.secret_id)
        )
        if self.last_response.status_code in [200, 201, 302]:
            return self._normalize_convertibles(self.last_response.json())
        raise LockFailure(
            "Error creating order", context={"raw_response": self.last_response}
        )

    def verify_transaction(self, session_id: str, amount: Union[Decimal, float], currency: Currency, order_id: int, **kwargs) -> ChargeResponse:
        url = urljoin(self.api_url, "/api/v1/transaction/verify")
        data = self._centify_convertibles({
          "merchantId": self.pos_id,
          "posId": self.pos_id,
          "sessionId": session_id,
          "amount": amount,
          "currency": currency.value,
          "orderId": order_id,
          "sign": self.get_sign({
                "sessionId": session_id,
                "orderId": order_id,
                "amount": self._centify(amount),
                "currency": currency.value,
            }),
        })
        headers = self._headers(**kwargs)
        data.update(kwargs)
        encoded = json.dumps(data, cls=DjangoJSONEncoder)
        self.last_response = requests.put(url, data=encoded, headers=headers)
        if self.last_response.status_code == 200:
            return self.last_response.json()
        raise ChargeFailure(
            "Error verifying transaction",
            context={"raw_response": self.last_response},
        )

    def get_transaction_info(self, session_id: str, **kwargs) -> TransactionInfoResponse:
        url = urljoin(self.api_url, f"/api/v1/transaction/by/sessionId/{session_id}")
        self.last_response = requests.get(url, headers=self._headers(**kwargs))
        if self.last_response.status_code == 200:
            return self._normalize_convertibles(self.last_response.json())
        raise CommunicationError(context={"raw_response": self.last_response})