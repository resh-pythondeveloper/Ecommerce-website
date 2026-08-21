from rest_framework import serializers

from apps.cart.models import Cart, CartItem
from apps.products.models import ProductVariant


class CartItemSerializer(serializers.ModelSerializer):

    sku = serializers.CharField(
        source="variant.sku",
        read_only=True
    )

    product_name = serializers.CharField(
        source="variant.product.name",
        read_only=True
    )

    price = serializers.DecimalField(
        source="variant.price",
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    discount_price = serializers.DecimalField(
        source="variant.discount_price",
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem

        fields = "__all__"

        read_only_fields = [
            "id",
            "sku",
            "product_name",
            "price",
            "discount_price",
            "created_at",
            "updated_at",
        ]

    def validate_quantity(self, value):

        if value <= 0:
            raise serializers.ValidationError(
                "Quantity must be greater than 0."
            )

        return value

class CartSerializer(serializers.ModelSerializer):

    items = CartItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Cart

        fields = [
            "id",
            "customer",
            "items",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "customer",
            "items",
            "created_at",
            "updated_at",
        ]