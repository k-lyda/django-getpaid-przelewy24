from typing import Optional

import swapper
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views import View
from getpaid.models import AbstractPayment


class Payment(AbstractPayment):
    external_id = models.IntegerField(
        _("external id"), blank=True, null=True, db_index=True
    )
    time_limit = models.IntegerField(_("time limit"), default=0)
    channel = models.IntegerField(_("payment channel"), default=16)
    token = models.CharField(_("token"), max_length=50, null=True)

    def verify_transaction(
        self,
        request: Optional[HttpRequest] = None,
        view: Optional[View] = None,
        **kwargs,
    ) -> HttpResponse:
        """
        Interfaces processor's :meth:`~getpaid_przelewy24.processor.Processor.verify_transaction`.
        """
        return self.processor.verify_transaction(request=request, view=None, **kwargs)

    class Meta(AbstractPayment.Meta):
        swappable = swapper.swappable_setting("getpaid", "Payment")
