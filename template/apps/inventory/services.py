from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.inventory.models import Inventory


class InventoryService:

    @staticmethod
    @transaction.atomic
    def update_stock(
        inventory,
        quantity
    ):

        if quantity < 0:

            raise ValidationError(
                "Stock quantity cannot be negative."
            )

        inventory.stock_quantity = quantity

        inventory.save(
            update_fields=[
                "stock_quantity",
                "updated_at"
            ]
        )

        return inventory

    @staticmethod
    @transaction.atomic
    def add_stock(inventory_id, quantity):

        if quantity <= 0:
            raise ValidationError(
                "Quantity must be greater than 0."
            )

        inventory = (
            Inventory.objects
            .select_for_update()
            .select_related(
                "variant",
                "variant__product"
            )
            .get(
                id=inventory_id,
                is_active=True
            )
        )

        inventory.stock_quantity += quantity

        inventory.save(
            update_fields=[
                "stock_quantity",
                "updated_at"
            ]
        )

        return inventory


    @staticmethod
    @transaction.atomic
    def remove_stock(inventory_id, quantity):

        if quantity <= 0:
            raise ValidationError(
                "Quantity must be greater than 0."
            )

        inventory = (
            Inventory.objects
            .select_for_update()
            .select_related(
                "variant",
                "variant__product"
            )
            .get(
                id=inventory_id,
                is_active=True
            )
        )

        if quantity > inventory.available_quantity:
            raise ValidationError(
                "Insufficient available stock."
            )

        inventory.stock_quantity -= quantity

        inventory.save(
            update_fields=[
                "stock_quantity",
                "updated_at"
            ]
        )

        return inventory