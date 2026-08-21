from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.core.exceptions import ValidationError

from apps.orders.models import Order

from apps.orders.serializers import (
    OrderCreateSerializer,
    OrderSerializer,
)

from apps.orders.services.order_service import (
    OrderService,
)


class OrderCreateAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        serializer = OrderCreateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            order = (
                OrderService.create_order(
                    user=request.user,

                    payment_method=(
                        serializer
                        .validated_data[
                            "payment_method"
                        ]
                    ),

                    shipping_address=(
                        serializer
                        .validated_data[
                            "shipping_address"
                        ]
                    ),

                    billing_address=(
                        serializer
                        .validated_data[
                            "billing_address"
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
                    "Order created successfully.",

                "data":
                    OrderSerializer(order).data,
            },
            status=status.HTTP_201_CREATED
        )


class OrderListAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        orders = (
            Order.objects
            .filter(
                user=request.user
            )
            .prefetch_related(
                "items",
                "addresses",
            )
        )

        serializer = OrderSerializer(
            orders,
            many=True
        )

        return Response(
            {
                "message":
                    "Orders retrieved successfully.",

                "data":
                    serializer.data,
            },
            status=status.HTTP_200_OK
        )


class OrderDetailAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request, pk):

        try:

            order = (
                Order.objects
                .filter(
                    user=request.user
                )
                .prefetch_related(
                    "items",
                    "addresses",
                )
                .get(
                    id=pk
                )
            )

        except Order.DoesNotExist:

            return Response(
                {
                    "message":
                        "Order not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderSerializer(
            order
        )

        return Response(
            {
                "message":
                    "Order retrieved successfully.",

                "data":
                    serializer.data,
            },
            status=status.HTTP_200_OK
        )