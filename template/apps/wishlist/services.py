from django.db import transaction

from apps.wishlist.models import (
    Wishlist,
    WishlistItem,
)
from apps.products.models import ProductVariant


class WishlistService:

    # ==========================================
    # GET OR CREATE WISHLIST
    # ==========================================

    @staticmethod
    def get_or_create_wishlist(customer):

        wishlist, created = Wishlist.objects.get_or_create(
            customer=customer
        )

        return wishlist

    # ==========================================
    # ADD VARIANT TO WISHLIST
    # ==========================================

    @staticmethod
    @transaction.atomic
    def add_item(customer, variant_id):

        variant = ProductVariant.objects.filter(
            id=variant_id,
            is_deleted=False,
            is_active=True
        ).first()

        if not variant:
            raise ValueError(
                "Product variant not found or inactive."
            )

        wishlist = WishlistService.get_or_create_wishlist(
            customer
        )

        item, created = WishlistItem.objects.get_or_create(
            wishlist=wishlist,
            variant=variant
        )

        return item, created

    # ==========================================
    # REMOVE VARIANT
    # ==========================================

    @staticmethod
    def remove_item(customer, variant_id):

        wishlist = Wishlist.objects.filter(
            customer=customer
        ).first()

        if not wishlist:
            return False

        deleted_count, _ = WishlistItem.objects.filter(
            wishlist=wishlist,
            variant_id=variant_id
        ).delete()

        return deleted_count > 0

    # ==========================================
    # CHECK WISHLIST
    # ==========================================

    @staticmethod
    def is_wishlisted(customer, variant_id):

        return WishlistItem.objects.filter(
            wishlist__customer=customer,
            variant_id=variant_id
        ).exists()

    # ==========================================
    # GET WISHLIST
    # ==========================================

    @staticmethod
    def get_wishlist(customer):

        wishlist = WishlistService.get_or_create_wishlist(
            customer
        )

        return (
            Wishlist.objects
            .prefetch_related(
                "items__variant__product"
            )
            .get(
                id=wishlist.id
            )
        )