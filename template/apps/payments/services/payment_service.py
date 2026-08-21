from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from apps.orders.models import Order
from apps.payments.models import Payment
from apps.payments.services.razorpay_service import (
    RazorpayService,
)

class PaymentService:

    @staticmethod
    @transaction.atomic
    def create_payment(
        *,
        user,
        order_id,
    ):

        # -----------------------------------------
        # 1. Get Order
        # -----------------------------------------

        try:

            order = (
                Order.objects
                .select_for_update()
                .get(
                    id=order_id,
                    user=user
                )
            )

        except Order.DoesNotExist:

            raise ValidationError(
                "Order not found."
            )

        # -----------------------------------------
        # 2. Check payment already exists
        # -----------------------------------------

        if hasattr(order, "payment"):

            payment = order.payment

            if payment.status == Payment.PaymentStatus.SUCCESS:

                raise ValidationError(
                    "Payment for this order "
                    "is already completed."
                )

            raise ValidationError(
                "Payment has already been created "
                "for this order."
            )

        # -----------------------------------------
        # 3. Check Order status
        # -----------------------------------------

        if order.status == Order.OrderStatus.CANCELLED:

            raise ValidationError(
                "Cannot make payment for "
                "a cancelled order."
            )

        # -----------------------------------------
        # 4. Check Order payment status
        # -----------------------------------------

        if (
            order.payment_status
            == Order.PaymentStatus.PAID
        ):

            raise ValidationError(
                "Order is already paid."
            )

        # -----------------------------------------
        # 5. Create Payment
        # -----------------------------------------

        payment = Payment.objects.create(

            order=order,

            amount=order.total_amount,

            payment_gateway="COD"
                if order.payment_method
                == Order.PaymentMethod.COD
                else None,

            status=Payment.PaymentStatus.CREATED,
        )

        return payment


    def create_razorpay_payment(
        *,
        user,
        order_id,
    ):

        # -----------------------------------------
        # 1. Get Order
        # -----------------------------------------

        try:

            order = (
                Order.objects
                .select_for_update()
                .get(
                    id=order_id,
                    user=user
                )
            )

        except Order.DoesNotExist:

            raise ValidationError(
                "Order not found."
            )

        # -----------------------------------------
        # 2. Validate Order
        # -----------------------------------------

        if (
            order.status
            == Order.OrderStatus.CANCELLED
        ):

            raise ValidationError(
                "Cannot pay for a cancelled order."
            )

        if (
            order.payment_status
            == Order.PaymentStatus.PAID
        ):

            raise ValidationError(
                "Order is already paid."
            )

        # -----------------------------------------
        # 3. Check existing payment
        # -----------------------------------------

        try:

            payment = order.payment

        except Payment.DoesNotExist:

            payment = None

        if payment:

            if (
                payment.status
                == Payment.PaymentStatus.SUCCESS
            ):

                raise ValidationError(
                    "Payment already completed."
                )

            if payment.razorpay_order_id:

                return payment

        # -----------------------------------------
        # 4. Create Razorpay Order
        # -----------------------------------------

        razorpay_order = (
            RazorpayService.create_order(
                amount=order.total_amount,
                receipt=order.order_number,
            )
        )

        # -----------------------------------------
        # 5. Create Local Payment
        # -----------------------------------------

        if payment is None:

            payment = Payment.objects.create(

                order=order,

                razorpay_order_id=(
                    razorpay_order["id"]
                ),

                payment_gateway="RAZORPAY",

                amount=order.total_amount,

                status=(
                    Payment.PaymentStatus.CREATED
                ),
            )

        else:

            payment.razorpay_order_id = (
                razorpay_order["id"]
            )

            payment.payment_gateway = (
                "RAZORPAY"
            )

            payment.amount = (
                order.total_amount
            )

            payment.status = (
                Payment.PaymentStatus.CREATED
            )

            payment.save()

        return payment

    # =========================================
    # VERIFY PAYMENT
    # =========================================

    @staticmethod
    @transaction.atomic
    def verify_razorpay_payment(
        *,
        user,
        razorpay_payment_id,
        razorpay_order_id,
        razorpay_signature,
    ):

        # -----------------------------------------
        # 1. Get Payment
        # -----------------------------------------

        try:

            payment = (
                Payment.objects
                .select_for_update()
                .select_related("order")
                .get(
                    razorpay_order_id=(
                        razorpay_order_id
                    )
                )
            )

        except Payment.DoesNotExist:

            raise ValidationError(
                "Payment not found."
            )

        order = payment.order

        # -----------------------------------------
        # 2. Verify User
        # -----------------------------------------

        if order.user_id != user.id:

            raise ValidationError(
                "You are not allowed to "
                "verify this payment."
            )

        # -----------------------------------------
        # 3. Already Paid
        # -----------------------------------------

        if (
            payment.status
            == Payment.PaymentStatus.SUCCESS
        ):

            return payment

        # -----------------------------------------
        # 4. Verify Razorpay Signature
        # -----------------------------------------

        try:

            RazorpayService.verify_payment(
                razorpay_order_id=(
                    payment.razorpay_order_id
                ),

                razorpay_payment_id=(
                    razorpay_payment_id
                ),

                razorpay_signature=(
                    razorpay_signature
                ),
            )

        except Exception:

            payment.status = (
                Payment.PaymentStatus.FAILED
            )

            payment.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            raise ValidationError(
                "Payment verification failed."
            )

        # -----------------------------------------
        # 5. Update Payment
        # -----------------------------------------

        payment.transaction_id = (
            razorpay_payment_id
        )

        payment.razorpay_signature = (
            razorpay_signature
        )

        payment.status = (
            Payment.PaymentStatus.SUCCESS
        )

        payment.paid_at = timezone.now()

        payment.save(
            update_fields=[
                "transaction_id",
                "razorpay_signature",
                "status",
                "paid_at",
                "updated_at",
            ]
        )

        # -----------------------------------------
        # 6. Update Order
        # -----------------------------------------

        order.payment_status = (
            Order.PaymentStatus.PAID
        )

        order.status = (
            Order.OrderStatus.CONFIRMED
        )

        order.save(
            update_fields=[
                "payment_status",
                "status",
                "updated_at",
            ]
        )

        return payment