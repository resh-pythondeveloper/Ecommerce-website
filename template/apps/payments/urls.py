from django.urls import path

from apps.payments.views import (
    PaymentCreateAPIView,RazorpayCreatePaymentAPIView,RazorpayVerifyPaymentAPIView
)


urlpatterns = [

    path(
        "create/",
        PaymentCreateAPIView.as_view()),
    path(
        "razorpay/create/",
        RazorpayCreatePaymentAPIView.as_view()
    ),

    path(
        "razorpay/verify/",
        RazorpayVerifyPaymentAPIView.as_view()
    ),

]