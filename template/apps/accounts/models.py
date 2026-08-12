from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from .managers import UserManager

class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        VENDOR = "VENDOR", "Vendor"
        CUSTOMER = "CUSTOMER", "Customer"

    class AuthType(models.TextChoices):
        PASSWORD = "PASSWORD", "Password"
        GOOGLE = "GOOGLE", "Google"
    username = models.CharField(
        max_length=150,null=True,blank=True,)
    
    email = models.EmailField(
        unique=True,null=True,blank=True,)

    mobile_number = models.CharField(
        max_length=15,unique=True,null=True,blank=True,)

    google_id = models.CharField(
        max_length=255,unique=True,null=True,blank=True,)

    auth_type = models.CharField(
        max_length=20,choices=AuthType.choices,default=AuthType.PASSWORD,)

    role = models.CharField(
        max_length=20,choices=Role.choices,default=Role.CUSTOMER,
    )

    is_email_verified = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )
    is_deleted = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table="app_user"


class OTPVerification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="otp_verifications",
    )

    otp = models.CharField(
        max_length=6,
    )

    expires_at = models.DateTimeField()

    is_verified = models.BooleanField(
        default=False,
    )

    attempts = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        db_table = "accounts_otp_verifications"