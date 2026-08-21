from rest_framework import serializers

from apps.inventory.models import Inventory


class InventorySerializer(serializers.ModelSerializer):

    available_quantity = serializers.IntegerField(
        read_only=True
    )

    is_low_stock = serializers.BooleanField(
        read_only=True
    )

    sku = serializers.CharField(
        source="variant.sku",
        read_only=True
    )

    product_name = serializers.CharField(
        source="variant.product.name",
        read_only=True
    )

    class Meta:
        model = Inventory

        fields = [
            "id",
            "variant",
            "sku",
            "product_name",
            "stock_quantity",
            "reserved_quantity",
            "available_quantity",
            "low_stock_threshold",
            "reorder_quantity",
            "is_low_stock",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "variant",
            "reserved_quantity",
            "available_quantity",
            "is_low_stock",
            "created_at",
            "updated_at",
        ]

    def validate_stock_quantity(self, value):

        if value < 0:
            raise serializers.ValidationError(
                "Stock quantity cannot be negative."
            )

        return value

    def validate_low_stock_threshold(self, value):

        if value < 0:
            raise serializers.ValidationError(
                "Low stock threshold cannot be negative."
            )

        return value

    def validate_reorder_quantity(self, value):

        if value < 1:
            raise serializers.ValidationError(
                "Reorder quantity must be greater than 0."
            )

        return value