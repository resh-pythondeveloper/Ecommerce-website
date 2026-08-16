from django.db import transaction
from apps.accounts.models import User,OTPVerification
from apps.customers.models import CustomerProfile
from apps.kam_management.models import KAM
from apps.vendors.models import VendorProfile
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
    def login_user(*,email,password,):

        # ---------------------------------
        # Find User by email or mobile
        # ---------------------------------

        user = User.objects.filter(
            email=email,
            is_deleted=False,
        ).first()

        if not user:
            raise ValidationError(
                "Invalid email or password."
            )

        # ---------------------------------
        # Check password
        # ---------------------------------

        if not user.check_password(password):
            raise ValidationError(
                "Invalid email/mobile or password."
            )

        # ---------------------------------
        # Account active?
        # ---------------------------------

        if not user.is_active:
            raise ValidationError(
                "Account is inactive."
            )

        # ---------------------------------
        # Email verification
        # ---------------------------------

        if not user.is_email_verified:
            raise ValidationError(
                "Please verify your email before login."
            )

        # ---------------------------------
        # Role-specific checks
        # ---------------------------------

        if user.role == User.Role.CUSTOMER:

            pass

        elif user.role == User.Role.KAM:

            kam = KAM.objects.filter(
                user=user,
                is_deleted=False,
                is_active=True,
            ).first()

            if not kam:
                raise ValidationError(
                    "KAM account is inactive."
                )

        elif user.role == User.Role.VENDOR:

            vendor = VendorProfile.objects.filter(
                user=user,
                is_deleted=False,
            ).first()

            if not vendor:
                raise ValidationError(
                    "Vendor profile not found."
                )

            if (
                vendor.approval_status
                != VendorProfile.ApprovalStatus.APPROVED
            ):
                if (
                    vendor.approval_status
                    == VendorProfile.ApprovalStatus.PENDING
                ):
                    raise ValidationError(
                        "Vendor account is waiting for approval."
                    )

                raise ValidationError(
                    "Vendor account has been rejected."
                )

        else:
            raise ValidationError(
                "Invalid user role."
            )

        return user
    
    @staticmethod
    def generate_tokens(user):

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }