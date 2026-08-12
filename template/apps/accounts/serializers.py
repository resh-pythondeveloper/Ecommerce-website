from rest_framework import serializers
from apps.accounts.models import User

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150
    )

    email = serializers.EmailField()

    mobile_number = serializers.CharField(
        max_length=15
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "mobile_number",
            "password",
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Email is already registered."
            )

        return value

    def validate_mobile_number(self, value):
        if User.objects.filter(
            mobile_number=value).exists():
            raise serializers.ValidationError(
                "Mobile number is already registered."
            )

        return value


class VerifyEmailSerializer(serializers.Serializer):

    email = serializers.EmailField()

    otp = serializers.CharField(
        min_length=6,
        max_length=6,
    )

class LoginSerializer(serializers.Serializer):

    email = serializers.CharField()

    password = serializers.CharField(
        write_only=True
    )