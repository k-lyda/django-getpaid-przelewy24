import swapper
from django.shortcuts import get_object_or_404
from getpaid.views import FallbackView


# TODO: Change to TemplateView with fancy loading screen to improve UX during waiting for verification
class VerificationView(FallbackView):
    def get_redirect_url(self, *args, **kwargs):
        Payment = swapper.load_model("getpaid", "Payment")
        payment = get_object_or_404(Payment, pk=self.kwargs["pk"])

        return payment.verify_transaction(kwargs)


verification = VerificationView.as_view()
