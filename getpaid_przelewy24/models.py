import swapper
from django.db import models
from django.utils.translation import ugettext_lazy as _
from getpaid.models import AbstractPayment


class Payment(AbstractPayment):
    time_limit = models.IntegerField(_("time limit"), default=0)
    channel = models.IntegerField(_("payment channel"))
    token = models.CharField(_("token"), max_length=50, null=True)

    class Meta(AbstractPayment.Meta):
        swappable = swapper.swappable_setting("getpaid", "Payment")