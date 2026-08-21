import razorpay

from django.conf import settings


class RazorpayService:

    @staticmethod
    def get_client():

        return razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET,
            )
        )

    @staticmethod
    def create_order(
        *,
        amount,
        receipt,
    ):

        client = (
            RazorpayService
            .get_client()
        )

        # Razorpay uses paise
        amount_in_paise = int(
            amount * 100
        )

        data = {
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": receipt,
        }

        razorpay_order = (
            client.order.create(
                data=data
            )
        )

        return razorpay_order

    @staticmethod
    def verify_payment(
        *,
        razorpay_order_id,
        razorpay_payment_id,
        razorpay_signature,
    ):

        client = (
            RazorpayService
            .get_client()
        )

        data = {
            "razorpay_order_id":
                razorpay_order_id,

            "razorpay_payment_id":
                razorpay_payment_id,

            "razorpay_signature":
                razorpay_signature,
        }

        client.utility.verify_payment_signature(
            data
        )

        return True