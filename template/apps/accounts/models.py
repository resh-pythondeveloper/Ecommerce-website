from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager

class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        VENDOR = "VENDOR", "Vendor"
        CUSTOMER = "CUSTOMER", "Customer"

    class AuthType(models.TextChoices):
        PASSWORD = "PASSWORD", "Password"
        GOOGLE = "GOOGLE", "Google"

    username = None

    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
    )

    mobile_number = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
    )

    google_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )

    auth_type = models.CharField(
        max_length=20,
        choices=AuthType.choices,
        default=AuthType.PASSWORD,
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )

    is_email_verified = models.BooleanField(
        default=False
    )

    is_mobile_verified = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table="app_user"