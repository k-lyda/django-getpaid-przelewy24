from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class GetpaidPrzelewy24Config(AppConfig):
    name = "getpaid_przelewy24"
    verbose_name = _("Przelewy24 backend")

    def ready(self):
        from getpaid.registry import registry

        registry.register(self.module)
