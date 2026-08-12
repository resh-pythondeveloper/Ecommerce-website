from django.db import transaction
from apps.accounts.models import User,OTPVerification
from apps.customers.models import CustomerProfile
from django.core.exceptions import ValidationError
from apps.accounts.services.otp_service import OTPService
from rest_framework_simplejwt.tokens import RefreshToken
class AuthService:

    @staticmethod
    @transaction.atomic
    def register_customer(*,username,email,mobile_number,password):
        user=User.objects.create_user(username=username,email=email,mobile_number=mobile_number,
            password=password,role=User.Role.CUSTOMER,auth_type=User.AuthType.PASSWORD,)
        otp = OTPService.create_otp(
            user=user)
        return user

    @staticmethod
    @transaction.atomic
    def verify_email(user,otp):

        OTPService.verify_otp(user=user,otp=otp)

        user.is_email_verified=True

        user.save(update_fields=["is_email_verified"])

        return True

    @staticmethod
    def login_customer(
        *,
        email,
        password,
    ):

        # Find user using email OR mobile
        user = User.objects.filter(
            email=email,
            is_deleted=False,
        ).first()

        if not user:
            raise ValidationError(
                "Invalid email/mobile or password."
            )

        # Make sure this is a customer
        if user.role != User.Role.CUSTOMER:
            raise ValidationError(
                "This account is not a customer account."
            )

        # Email must be verified
        if not user.is_email_verified:
            raise ValidationError(
                "Please verify your email before login."
            )

        # Check password
        if not user.check_password(password):
            raise ValidationError(
                "Invalid email/mobile or password."
            )

        return user
    
    @staticmethod
    def generate_tokens(user):

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }