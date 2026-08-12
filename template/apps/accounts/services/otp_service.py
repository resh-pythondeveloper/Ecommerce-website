import secrets
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import OTPVerification
from django.core.exceptions import ValidationError
from apps.accounts.services.notification_service import NotificationService

class OTPService:
    @staticmethod
    def generate_otp():
        return str(secrets.randbelow(900000)+100000)

    @staticmethod
    def create_otp(*,user):
        otp=OTPService.generate_otp()

        OTPVerification.objects.filter(
            user=user
        ).delete()

        OTPVerification.objects.create(
            user=user,
            otp=otp,
            expires_at=(timezone.now()+ timedelta(minutes=5)))

        NotificationService.send_email_otp(
                email=user.email,
                otp=otp,)

        return otp

    @staticmethod
    def verify_otp(user,otp):
        verification=OTPVerification.objects.filter(user=user).order_by("-created_at").first()

        if not verification:
            raise ValidationError("otp not found")
        
        if verification.expires_at<timezone.now():
            raise ValidationError("otp has expired")

        if verification.attempts >= 5:
            raise ValidationError(
                "Maximum OTP attempts exceeded."
            )

        if verification.otp!=otp:
            verification.attempts+=1
            verification.save(update_fields=["attempts"])
            raise ValidationError("invalid OTP")
        
        verification.delete()
        return True
    
    @staticmethod
    def resend_otp(*, user):

        # Delete existing OTP
        OTPVerification.objects.filter(
            user=user
        ).delete()

        # Generate new OTP
        otp = OTPService.generate_otp()

        # Create new OTP
        OTPVerification.objects.create(
            user=user,
            otp=otp,
            expires_at=(
                timezone.now()
                + timedelta(minutes=5)
            ),
        )

        # Send new OTP
        NotificationService.send_email_otp(
            email=user.email,
            otp=otp,
        )

        return otp