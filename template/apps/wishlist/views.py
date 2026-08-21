from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.customers.models import CustomerProfile
from apps.wishlist.serializers import WishlistSerializer
from apps.wishlist.services import WishlistService


class WishlistView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    # ==========================================
    # GET WISHLIST
    # ==========================================

    def get(self, request, variant_id=None):

        try:
            customer = CustomerProfile.objects.get(
                user=request.user
            )

        except CustomerProfile.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Customer profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        if variant_id:
            is_wishlisted = WishlistService.is_wishlisted(
                            customer=customer,
                            variant_id=variant_id
                        )
                
            return Response(
                            {
                                "success": True,
                                "variant_id": variant_id,
                                "is_wishlisted": is_wishlisted
                            },status=status.HTTP_200_OK)

        wishlist = WishlistService.get_wishlist(
            customer
        )

        serializer = WishlistSerializer(
            wishlist
        )

        return Response(
            {
                "success": True,
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    # ==========================================
    # ADD TO WISHLIST
    # ==========================================

    def post(self, request):

        try:
            customer = CustomerProfile.objects.get(
                user=request.user
            )

        except CustomerProfile.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Customer profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        variant_id = request.data.get(
            "variant_id"
        )

        if not variant_id:

            return Response(
                {
                    "success": False,
                    "message": "variant_id is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            item, created = WishlistService.add_item(
                customer=customer,
                variant_id=variant_id
            )

        except ValueError as e:

            return Response(
                {
                    "success": False,
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not created:

            return Response(
                {
                    "success": False,
                    "message": "Product already exists in wishlist."
                },
                status=status.HTTP_409_CONFLICT
            )

        return Response(
            {
                "success": True,
                "message": "Product added to wishlist.",
                "data": {
                    "id": item.id,
                    "variant_id": item.variant_id
                }
            },
            status=status.HTTP_201_CREATED
        )

    # ==========================================
    # REMOVE FROM WISHLIST
    # ==========================================

    def delete(self, request, variant_id):

        try:
            customer = CustomerProfile.objects.get(
                user=request.user
            )

        except CustomerProfile.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Customer profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        deleted = WishlistService.remove_item(
            customer=customer,
            variant_id=variant_id
        )

        if not deleted:

            return Response(
                {
                    "success": False,
                    "message": "Product not found in wishlist."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "success": True,
                "message": "Product removed from wishlist."
            },
            status=status.HTTP_200_OK
        )


    