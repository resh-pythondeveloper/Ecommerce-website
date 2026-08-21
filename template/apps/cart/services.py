from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.cart.models import Cart, CartItem
from apps.customers.models import CustomerProfile
from apps.products.models import ProductVariant


class CartService:

    @staticmethod
    def get_or_create_cart(customer):
        """
        Get existing cart or create a new cart
        for the customer.
        """

        cart, created = Cart.objects.get_or_create(
            customer=customer
        )

        return cart

    @staticmethod
    @transaction.atomic
    def add_item(customer, variant_id, quantity):
        """
        Add a product variant to the customer's cart.
        """

        if quantity <= 0:
            raise ValidationError(
                "Quantity must be greater than 0."
            )

        # Get active variant
        variant = ProductVariant.objects.filter(
            id=variant_id,
            is_active=True,
            is_deleted=False,
            product__is_active=True,
            product__is_deleted=False,
        ).select_related(
            "product"
        ).first()

        if not variant:
            raise ValidationError(
                "Product variant does not exist or is inactive."
            )

        # Get customer's cart
        cart = CartService.get_or_create_cart(
            customer
        )

        # Check existing item
        cart_item = CartItem.objects.filter(
            cart=cart,
            variant=variant
        ).first()

        if cart_item:

            new_quantity = (
                cart_item.quantity + quantity
            )

            cart_item.quantity = new_quantity

            cart_item.save(
                update_fields=[
                    "quantity",
                    "updated_at"
                ]
            )

        else:

            cart_item = CartItem.objects.create(
                cart=cart,
                variant=variant,
                quantity=quantity
            )

        return cart_item

    @staticmethod
    @transaction.atomic
    def update_item_quantity(
        customer,
        item_id,
        quantity
    ):
        """
        Update quantity of an existing cart item.
        """

        if quantity <= 0:
            raise ValidationError(
                "Quantity must be greater than 0."
            )

        cart = CartService.get_or_create_cart(
            customer
        )

        cart_item = CartItem.objects.filter(
            id=item_id,
            cart=cart
        ).first()

        if not cart_item:
            raise ValidationError(
                "Cart item not found."
            )

        cart_item.quantity = quantity

        cart_item.save(
            update_fields=[
                "quantity",
                "updated_at"
            ]
        )

        return cart_item

    @staticmethod
    @transaction.atomic
    def remove_item(customer, item_id):
        """
        Remove an item from the customer's cart.
        """

        cart = CartService.get_or_create_cart(
            customer
        )

        cart_item = CartItem.objects.filter(
            id=item_id,
            cart=cart
        ).first()

        if not cart_item:
            raise ValidationError(
                "Cart item not found."
            )

        cart_item.delete()

        return True

    @staticmethod
    @transaction.atomic
    def clear_cart(customer):
        """
        Remove all items from customer's cart.
        """

        cart = CartService.get_or_create_cart(
            customer
        )

        cart.items.all().delete()

        return cart