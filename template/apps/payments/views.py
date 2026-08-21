from django.core.exceptions import ValidationError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings
from apps.payments.serializers import (PaymentVerifySerializer,
    PaymentCreateSerializer,
    PaymentSerializer,
)

from template.apps.payments.services.payment_service import (
    PaymentService,
)


class PaymentCreateAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        serializer = PaymentCreateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            payment = (
                PaymentService.create_payment(
                    user=request.user,

                    order_id=(
                        serializer
                        .validated_data[
                            "order_id"
                        ]
                    ),
                )
            )

        except ValidationError as exc:

            return Response(
                {
                    "message": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message":
                    "Payment created successfully.",

                "data":
                    PaymentSerializer(
                        payment
                    ).data,
            },
            status=status.HTTP_201_CREATED
        )

class RazorpayCreatePaymentAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        serializer = (
            PaymentCreateSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )
        try:

            payment = (
                PaymentService
                .create_razorpay_payment(

                    user=request.user,

                    order_id=(
                        serializer
                        .validated_data[
                            "order_id"
                        ]
                    ),
                )
            )
        except ValidationError as exc:

            return Response(
                {
                    "message": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                "message":
            "Razorpay payment created.",

        "data": {
            "payment_id":
                payment.id,

            "order_id":
                payment.order.id,

            "razorpay_order_id":
                payment.razorpay_order_id,

            "amount":
                payment.amount,

            "amount_in_paise":
                int(payment.amount * 100),

            "currency":
                "INR",

            "razorpay_key_id":
                settings.RAZORPAY_KEY_ID,
 
                }
            },
            status=status.HTTP_201_CREATED
        )


class RazorpayVerifyPaymentAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        serializer = (
            PaymentVerifySerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            payment = (
                PaymentService
                .verify_razorpay_payment(

                    user=request.user,

                    razorpay_payment_id=(
                        serializer
                        .validated_data[
                            "razorpay_payment_id"
                        ]
                    ),

                    razorpay_order_id=(
                        serializer
                        .validated_data[
                            "razorpay_order_id"
                        ]
                    ),

                    razorpay_signature=(
                        serializer
                        .validated_data[
                            "razorpay_signature"
                        ]
                    ),
                )
            )

        except ValidationError as exc:

            return Response(
                {
                    "message": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message":
                    "Payment verified successfully.",

                "data":
                    PaymentSerializer(
                        payment
                    ).data,
            },
            status=status.HTTP_200_OK
        )