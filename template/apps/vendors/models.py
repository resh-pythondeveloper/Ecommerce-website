from django.conf import settings
from django.db import models
from apps.kam_management.models import KAM

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
    vendor_id = models.CharField(
        max_length=50,
        unique=True
    )
    profile_picture = models.JSONField(
        default=list,
        blank=True
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
    gst_number = models.CharField(
        max_length=50,
        blank=True,
        null=True
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
    is_deleted = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    kam=models.ForeignKey(KAM,on_delete=models.SET_NULL,null=True,blank=True,related_name="vendors")

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table="vendors"

    def save(self, *args, **kwargs):

        if not self.vendor_id:

            last_vendor = (
                VendorProfile.objects
                .order_by("-id")
                .first()
            )

            if last_vendor:
                number = int(
                    last_vendor.vendor_id.replace(
                        "VENDOR",
                        ""
                    )
                )
                next_number = number + 1
            else:
                next_number = 1

            self.vendor_id = (
                f"VENDOR{next_number:04d}"
            )

        super().save(*args, **kwargs)