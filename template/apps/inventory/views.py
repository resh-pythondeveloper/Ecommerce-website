from django.shortcuts import get_object_or_404
from django.db.models import F

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.inventory.models import Inventory
from apps.inventory.serializers import InventorySerializer
from apps.inventory.services import InventoryService

from apps.products.models import ProductVariant


class InventoryView(APIView):

    # ==========================================
    # LIST INVENTORY
    # ==========================================

    def get(self, request):

        inventories = Inventory.objects.filter(
            is_active=True
        ).select_related(
            "variant",
            "variant__product"
        ).order_by(
            "-created_at"
        )

        serializer = InventorySerializer(
            inventories,
            many=True
        )

        return Response(
            {
                "success": True,
                "count": inventories.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK
        )


class InventoryDetailView(APIView):

    # ==========================================
    # GET INVENTORY
    # ==========================================

    def get(self, request, variant_id):

        inventory = get_object_or_404(
            Inventory,
            variant_id=variant_id,
            is_active=True
        )

        serializer = InventorySerializer(
            inventory
        )

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    # ==========================================
    # UPDATE STOCK
    # ==========================================

    def patch(self, request, variant_id):

        inventory = get_object_or_404(
            Inventory,
            variant_id=variant_id,
            is_active=True
        )

        serializer = InventorySerializer(
            inventory,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        inventory = serializer.save()

        return Response(
            {
                "success": True,
                "message": "Inventory updated successfully",
                "data": InventorySerializer(
                    inventory
                ).data,
            },
            status=status.HTTP_200_OK
        )


class InventoryAddStockView(APIView):

    def post(self, request, variant_id):

        inventory = get_object_or_404(
            Inventory,
            variant_id=variant_id,
            is_active=True
        )

        quantity = request.data.get("quantity")

        if quantity is None:
            return Response(
                {
                    "success": False,
                    "message": "Quantity is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)

        except (TypeError, ValueError):
            return Response(
                {
                    "success": False,
                    "message": "Quantity must be an integer."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        inventory = InventoryService.add_stock(
            inventory.id,
            quantity
        )

        return Response(
            {
                "success": True,
                "message": "Stock added successfully",
                "data": InventorySerializer(
                    inventory
                ).data,
            },
            status=status.HTTP_200_OK
        )


class InventoryRemoveStockView(APIView):

    def post(self, request, variant_id):

        inventory = get_object_or_404(
            Inventory,
            variant_id=variant_id,
            is_active=True
        )

        quantity = request.data.get("quantity")

        if quantity is None:
            return Response(
                {
                    "success": False,
                    "message": "Quantity is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)

        except (TypeError, ValueError):
            return Response(
                {
                    "success": False,
                    "message": "Quantity must be an integer."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        inventory = InventoryService.remove_stock(
            inventory.id,
            quantity
        )

        return Response(
            {
                "success": True,
                "message": "Stock removed successfully",
                "data": InventorySerializer(
                    inventory
                ).data,
            },
            status=status.HTTP_200_OK
        )