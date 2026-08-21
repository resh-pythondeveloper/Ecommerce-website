from rest_framework import serializers

from apps.orders.models import (
    Order,
    OrderItem,
    OrderAddress,
)


class OrderAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderAddress

        fields = [
            "id",
            "address_type",
            "full_name",
            "mobile_number",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "country",
            "pincode",
        ]

        read_only_fields = [
            "id",
            "address_type",
        ]


class OrderItemSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = OrderItem

        fields = [
            "id",
            "product",
            "variant",
            "product_name",
            "sku",
            "quantity",
            "price",
            "discount_price",
            "discount_amount",
            "tax_rate",
            "tax_amount",
            "total_price",
        ]

        read_only_fields = fields


class OrderSerializer(
    serializers.ModelSerializer
):

    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    addresses = OrderAddressSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order

        fields = [
            "id",
            "order_number",
            "status",
            "payment_method",
            "payment_status",
            "subtotal",
            "discount",
            "shipping_charge",
            "tax",
            "total_amount",
            "items",
            "addresses",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields


class OrderCreateSerializer(
    serializers.Serializer
):

    payment_method = serializers.ChoiceField(
        choices=Order.PaymentMethod.choices
    )

    shipping_address = OrderAddressSerializer()

    billing_address = OrderAddressSerializer(
        required=False
    )

    same_as_shipping = serializers.BooleanField(
        default=True
    )

    def validate(self, attrs):

        shipping_address = (
            attrs["shipping_address"]
        )

        billing_address = (
            attrs.get("billing_address")
        )

        same_as_shipping = (
            attrs["same_as_shipping"]
        )

        # address_type is controlled by backend
        shipping_address.pop(
            "address_type",
            None
        )
        if same_as_shipping:

            attrs["billing_address"] = (
                shipping_address.copy()
            )

        else:

            if not billing_address:

                raise serializers.ValidationError(
                    {
                        "billing_address":
                        "Billing address is required."
                    }
                )

            billing_address.pop(
                "address_type",
                None
            )

        return attrs