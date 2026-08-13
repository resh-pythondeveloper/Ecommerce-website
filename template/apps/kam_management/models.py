from django.conf import settings
from django.db import models


class KAM(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="kam_profile",
    )

    kam_id = models.CharField(
        max_length=50,
        unique=True,
    )
    profile_picture = models.JSONField(default=list, blank=True)

    first_name = models.CharField(
        max_length=100,
    )

    last_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    is_deleted = models.BooleanField(
        default=False,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "kam"

    def save(self, *args, **kwargs):

        if not self.kam_id:

            last_kam = (
                KAM.objects
                .order_by("-id")
                .first()
            )

            if last_kam:
                last_number = int(
                    last_kam.kam_id.replace("KAM", "")
                )
                next_number = last_number + 1
            else:
                next_number = 1

            self.kam_id = f"KAM{next_number:04d}"

        super().save(*args, **kwargs)