from rest_framework import serializers

from apps.wishlist.models import (
    Wishlist,
    WishlistItem,
)


class WishlistItemSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source="variant.product.name",
        read_only=True
    )

    sku = serializers.CharField(
        source="variant.sku",
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
        model = WishlistItem

        fields = [
            "id",
            "variant",
            "product_name",
            "sku",
            "price",
            "discount_price",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]


class WishlistSerializer(serializers.ModelSerializer):

    items = WishlistItemSerializer(
        many=True,
        read_only=True
    )

    item_count = serializers.IntegerField(
        source="items.count",
        read_only=True
    )

    class Meta:
        model = Wishlist

        fields = [
            "id",
            "items",
            "item_count",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]