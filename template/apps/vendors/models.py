from django.conf import settings
from django.db import models


class VendorProfile(models.Model):

    class ApprovalStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vendor_profile",
    )

    store_name = models.CharField(
        max_length=200
    )

    business_name = models.CharField(
        max_length=200,
        blank=True,
    )

    business_email = models.EmailField(
        blank=True,
    )

    business_phone = models.CharField(
        max_length=15,
        blank=True,
    )

    business_address = models.TextField(
        blank=True,
    )

    logo = models.JSONField(
        null=True,
        blank=True,
    )

    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table="vendors"