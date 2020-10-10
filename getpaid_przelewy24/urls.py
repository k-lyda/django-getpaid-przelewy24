from django.urls import path

from . import views

app_name = "getpaid_przelewy24"

urlpatterns = [
    path("verify/<uuid:pk>/", views.verification, name="payment-verification",),
]
