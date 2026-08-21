from decimal import (
    Decimal,
    ROUND_HALF_UP,
)

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from apps.inventory.models import Inventory
from apps.cart.models import Cart
from apps.orders.models import (
    Order,
    OrderItem,
    OrderAddress,
)


class OrderService:

    TAX_RATE = Decimal("18.00")

    FREE_SHIPPING_AMOUNT = Decimal("1000.00")

    SHIPPING_CHARGE = Decimal("50.00")

    @staticmethod
    @transaction.atomic
    def create_order(
        *,
        user,
        payment_method,
        shipping_address,
        billing_address,
    ):

        # -----------------------------------------
        # 1. Get Customer Profile
        # -----------------------------------------

        try:
            customer = user.customer_profile

        except AttributeError:
            raise ValidationError(
                "Customer profile not found."
            )

        # -----------------------------------------
        # 2. Get Cart
        # -----------------------------------------

        try:

            cart = (
                Cart.objects
                .prefetch_related(
                    "items__variant__product","items__variant__inventory",
                )
                .get(
                    customer=customer
                )
            )

        except Cart.DoesNotExist:

            raise ValidationError(
                "Cart not found."
            )

        # -----------------------------------------
        # 3. Get Cart Items
        # -----------------------------------------

        cart_items = cart.items.all()

        if not cart_items.exists():

            raise ValidationError(
                "Your cart is empty."
            )

        # -----------------------------------------
        # 4. Initialize totals
        # -----------------------------------------

        subtotal = Decimal("0.00")

        total_discount = Decimal("0.00")

        total_tax = Decimal("0.00")

        order_items_data = []

        # -----------------------------------------
        # 5. Process Cart Items
        # -----------------------------------------

        for cart_item in cart_items:

            variant = cart_item.variant

            product = variant.product

            quantity = cart_item.quantity

            # -------------------------------------
            # Product validation
            # -------------------------------------

            if product.is_deleted:

                raise ValidationError(
                    f"{product.name} "
                    f"is no longer available."
                )

            # -------------------------------------
            # Variant validation
            # -------------------------------------

            if variant.is_deleted:

                raise ValidationError(
                    f"{variant.sku} "
                    f"is no longer available."
                )

            if not variant.is_active:

                raise ValidationError(
                    f"{variant.sku} "
                    f"is inactive."
                )

            # -------------------------------------
            # Stock validation
            # -------------------------------------

            try:
                inventory = variant.inventory
            except Inventory.DoesNotExist:
                raise ValidationError(
                    f"Inventory not found for {variant.sku}."
                )

            available_quantity = inventory.available_quantity

            if available_quantity < quantity:
                raise ValidationError(
                    f"Only {available_quantity} "
                    f"items available for {variant.sku}."
                )

            # -------------------------------------
            # Original price
            # -------------------------------------

            original_price = variant.price

            # -------------------------------------
            # Selling price
            # -------------------------------------

            if variant.discount_price is not None:

                selling_price = (
                    variant.discount_price
                )

            else:

                selling_price = (
                    variant.price
                )

            # -------------------------------------
            # Validate discount
            # -------------------------------------

            if selling_price > original_price:

                raise ValidationError(
                    f"Discount price cannot be "
                    f"greater than price for "
                    f"{variant.sku}."
                )

            # -------------------------------------
            # Discount
            # -------------------------------------

            discount_per_item = (
                original_price
                - selling_price
            )

            discount_amount = (
                discount_per_item
                * quantity
            )

            # -------------------------------------
            # Item subtotal
            # -------------------------------------

            item_subtotal = (
                selling_price
                * quantity
            )

            # -------------------------------------
            # Tax
            # -------------------------------------

            tax_rate = OrderService.TAX_RATE

            tax_amount = (
                item_subtotal
                * tax_rate
                / Decimal("100")
            )

            tax_amount = tax_amount.quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )

            # -------------------------------------
            # Item total
            # -------------------------------------

            item_total = (
                item_subtotal
                + tax_amount
            )

            # -------------------------------------
            # Add totals
            # -------------------------------------

            subtotal += item_subtotal

            total_discount += discount_amount

            total_tax += tax_amount

            # -------------------------------------
            # Prepare OrderItem
            # -------------------------------------

            order_items_data.append(
                {
                    "product": product,
                    "variant": variant,
                    "product_name": product.name,
                    "sku": variant.sku,
                    "quantity": quantity,
                    "price": original_price,
                    "discount_price": (
                        variant.discount_price
                    ),
                    "discount_amount": (
                        discount_amount
                    ),
                    "tax_rate": tax_rate,
                    "tax_amount": tax_amount,
                    "total_price": item_total,
                }
            )

        # -----------------------------------------
        # 6. Shipping
        # -----------------------------------------

        shipping_charge = (
            OrderService.calculate_shipping(
                subtotal=subtotal
            )
        )

        # -----------------------------------------
        # 7. Final Total
        # -----------------------------------------

        total_amount = (
            subtotal
            + total_tax
            + shipping_charge
        )

        total_amount = total_amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        # -----------------------------------------
        # 8. Order Status
        # -----------------------------------------

        if (
            payment_method
            == Order.PaymentMethod.COD
        ):

            order_status = (
                Order.OrderStatus.CONFIRMED
            )

        else:

            order_status = (
                Order.OrderStatus.PENDING
            )

        # -----------------------------------------
        # 9. Create Order
        # -----------------------------------------

        order = Order.objects.create(

            user=user,

            payment_method=payment_method,

            status=order_status,

            payment_status=(
                Order.PaymentStatus.PENDING
            ),

            subtotal=subtotal,

            discount=total_discount,

            shipping_charge=shipping_charge,

            tax=total_tax,

            total_amount=total_amount,
        )

        # -----------------------------------------
        # 10. Create Order Items
        # -----------------------------------------

        order_items = []

        for item_data in order_items_data:

            order_items.append(
                OrderItem(
                    order=order,
                    **item_data
                )
            )

        OrderItem.objects.bulk_create(
            order_items
        )

        # -----------------------------------------
        # 11. Shipping Address
        # -----------------------------------------

        OrderAddress.objects.create(

            order=order,

            address_type=(
                OrderAddress
                .AddressType
                .SHIPPING
            ),

            **shipping_address
        )

        # -----------------------------------------
        # 12. Billing Address
        # -----------------------------------------

        OrderAddress.objects.create(

            order=order,

            address_type=(
                OrderAddress
                .AddressType
                .BILLING
            ),

            **billing_address
        )

        # -----------------------------------------
        # 13. Reduce Stock
        # -----------------------------------------

        for cart_item in cart_items:

            variant = cart_item.variant

            updated = (
                Inventory.objects
                .filter(
                    variant=variant,
                    stock_quantity__gte=cart_item.quantity,
                )
                .update(
                    stock_quantity=F("stock_quantity")
                    - cart_item.quantity
                )
            )

            if updated == 0:

                raise ValidationError(
                    f"Insufficient stock for "
                    f"{variant.sku}."
                )

        # -----------------------------------------
        # 14. Clear Cart Items
        # -----------------------------------------

        cart_items.delete()

        return order

    # -----------------------------------------
    # Shipping Calculation
    # -----------------------------------------

    @staticmethod
    def calculate_shipping(*, subtotal):

        if (
            subtotal
            >= OrderService.FREE_SHIPPING_AMOUNT
        ):

            return Decimal("0.00")

        return OrderService.SHIPPING_CHARGE