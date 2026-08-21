from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.cart.models import Cart, CartItem
from apps.cart.serializers import (
    CartSerializer,
    CartItemSerializer,
)
from apps.customers.models import CustomerProfile
from apps.cart.services import CartService


class CartView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    # ==========================================
    # GET CART
    # ==========================================

    def get(self, request):

        try:
            customer=CustomerProfile.objects.get(user=request.user)
        except CustomerProfile.DoesNotExist:
            return Response(
                            {
                                "success": False,
                                "message": "Customer profile not found."
                            },
                            status=status.HTTP_404_NOT_FOUND
                        )
            

        cart = CartService.get_or_create_cart(
            customer
        )

        cart = (
            Cart.objects
            .prefetch_related(
                "items__variant__product"
            )
            .get(
                id=cart.id
            ))

        serializer = CartSerializer(cart)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    # ==========================================
    # ADD ITEM TO CART
    # ==========================================

    def post(self, request):

        try:
                customer=CustomerProfile.objects.get(user=request.user)
        except CustomerProfile.DoesNotExist:
            return Response(
                                    {
                                        "success": False,
                                        "message": "Customer profile not found."
                                    },
                                    status=status.HTTP_404_NOT_FOUND
                                )

        variant_id = request.data.get(
            "variant"
        )

        quantity = request.data.get(
            "quantity",
            1
        )

        if not variant_id:

            return Response(
                {
                    "success": False,
                    "message": "Variant is required.",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)

        except (TypeError, ValueError):

            return Response(
                {
                    "success": False,
                    "message": "Quantity must be a valid number.",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item = CartService.add_item(
            customer=customer,
            variant_id=variant_id,
            quantity=quantity
        )

        return Response(
            {
                "success": True,
                "message": "Product added to cart successfully.",
                "data": CartItemSerializer(
                    cart_item
                ).data,
            },
            status=status.HTTP_201_CREATED
        )


class CartItemView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    # ==========================================
    # UPDATE QUANTITY
    # ==========================================

    def patch(self, request, item_id):

        try:
            customer=CustomerProfile.objects.get(user=request.user)
        except CustomerProfile.DoesNotExist:
            return Response({"success": False,
                            "message": "Customer profile not found."},status=status.HTTP_404_NOT_FOUND)

        quantity = request.data.get(
            "quantity"
        )

        if quantity is None:

            return Response(
                {
                    "success": False,
                    "message": "Quantity is required.",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)

        except (TypeError, ValueError):

            return Response(
                {
                    "success": False,
                    "message": "Quantity must be a valid number.",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item = CartService.update_item_quantity(
            customer=customer,
            item_id=item_id,
            quantity=quantity
        )

        return Response(
            {
                "success": True,
                "message": "Cart quantity updated successfully.",
                "data": CartItemSerializer(
                    cart_item
                ).data,
            },
            status=status.HTTP_200_OK
        )

    # ==========================================
    # REMOVE ITEM
    # ==========================================

    def delete(self, request, item_id):

        try:
            customer=CustomerProfile.objects.get(user=request.user)
        except CustomerProfile.DoesNotExist:
            return Response({"success": False,
                            "message": "Customer profile not found."},
                            status=status.HTTP_404_NOT_FOUND)

        CartService.remove_item(
            customer=customer,
            item_id=item_id
        )

        return Response(
            {
                "success": True,
                "message": "Item removed from cart successfully.",
            },
            status=status.HTTP_200_OK
        )


class CartClearView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    # ==========================================
    # CLEAR CART
    # ==========================================

    def delete(self, request):

        try:
            customer=CustomerProfile.objects.get(user=request.user)
        except CustomerProfile.DoesNotExist:
            return Response({"success": False,
                                    "message": "Customer profile not found."},status=status.HTTP_404_NOT_FOUND)

        CartService.clear_cart(
            customer
        )

        return Response(
            {
                "success": True,
                "message": "Cart cleared successfully.",
            },
            status=status.HTTP_200_OK
        )