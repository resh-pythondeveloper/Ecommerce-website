from rest_framework import serializers

from apps.payments.models import Payment


class PaymentCreateSerializer(serializers.Serializer):

    order_id = serializers.IntegerField()

class PaymentVerifySerializer(serializers.Serializer):

    razorpay_payment_id = serializers.CharField()

    razorpay_order_id = serializers.CharField()

    razorpay_signature = serializers.CharField()


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment

        fields = "__all__"

        read_only_fields = fields