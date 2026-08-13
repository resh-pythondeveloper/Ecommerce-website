from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import User
from apps.accounts.services.otp_service import OTPService


class AdminAuthService:

    @staticmethod
    def login(*, email, password):

        user = User.objects.filter(
            email=email,
            role=User.Role.ADMIN,
            is_deleted=False,
        ).first()

        if not user:
            raise ValidationError(
                "Invalid admin credentials."
            )

        if not user.is_active:
            raise ValidationError(
                "Admin account is inactive."
            )

        if not user.check_password(password):
            raise ValidationError(
                "Invalid admin credentials."
            )

        # Generate OTP
        OTPService.create_otp(
            user=user
        )

        return user

    @staticmethod
    def verify_otp(*, email, otp):

        user = User.objects.filter(
            email=email,
            role=User.Role.ADMIN,
            is_deleted=False,
        ).first()

        if not user:
            raise ValidationError(
                "Admin not found."
            )

        OTPService.verify_otp(
            user=user,
            otp=otp
        )

        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }