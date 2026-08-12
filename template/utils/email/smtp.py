from django.conf import settings
from django.core.mail import send_mail
import requests

def send_otp_email(
    *,
    email: str,
    otp: str,
) -> None:

    subject = "Your E-Commerce Verification OTP"

    message = (
        f"Your OTP is {otp}.\n\n"
        "This OTP is valid for 5 minutes.\n"
        "Please do not share this OTP with anyone."
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
