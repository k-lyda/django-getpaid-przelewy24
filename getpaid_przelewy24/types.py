from enum import Enum, auto, IntFlag
from enum import Enum, auto, IntFlag
from typing import Any, Optional, Union, NamedTuple

from typing_extensions import TypedDict


class AutoName(str, Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name.strip("_")




class PayTypeValue(AutoName):
    PBL = auto()
    CARD_TOKEN = auto()
    INSTALLMENTS = auto()


class SpecData(TypedDict):
    name: str
    value: Any


class Currency(AutoName):
    EUR = auto()
    PLN = auto()


class PaymentChannel(IntFlag):
    CARDS = 1
    BANK_TRANSFER = 2
    BANK_TRANSFER_STANDARD = 4
    N_A = 8
    ALL = 16
    PREPAYMENT = 32
    PAY_BY_LINK = 64
    INSTALLMENT = 128
    DIGITAL_WALLETS = 256


class Language(AutoName):
    pl = auto()
    en = auto()
    cs = auto()
    bg = auto()
    da = auto()
    de = auto()
    el = auto()
    es = auto()
    et = auto()
    fi = auto()
    fr = auto()
    hr = auto()
    hu = auto()
    it = auto()
    lt = auto()
    lv = auto()
    pt = auto()
    ro = auto()
    ru = auto()
    sk = auto()
    sl = auto()
    sr = auto()
    sv = auto()
    tr = auto()
    uk = auto()


class BuyerData(NamedTuple):
    email: str
    customerIp: Optional[str] = None
    extCustomerId: Optional[Union[str, int]] = None
    phone: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    nin: Optional[str] = None
    language: Optional[Language] = None

    def __str__(self):
        if self.firstName and self.lastName:
            return str(f"{self.firstName} {self.lastName}")
        else:
            return self.email


class ResponseStatus(AutoName):
    SUCCESS = auto()
    WARNING_CONTINUE_REDIRECT = auto()
    WARNING_CONTINUE_3DS = auto()
    WARNING_CONTINUE_CVV = auto()


class OrderStatus(AutoName):
    NEW = auto()
    PENDING = auto()
    CANCELED = auto()
    COMPLETED = auto()
    WAITING_FOR_CONFIRMATION = auto()
