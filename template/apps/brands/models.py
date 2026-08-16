from django.db import models
from django.utils.text import slugify
# Create your models here.
class Brand(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True)

    slug = models.SlugField(
        max_length=180,
        unique=True,
        blank=True)

    description = models.TextField(
        blank=True,
        null=True)

    image = models.JSONField(
        blank=True,
        null=True)

    is_deleted = models.BooleanField(
        default=False)

    created_at = models.DateTimeField(
        auto_now_add=True)

    updated_at = models.DateTimeField(
        auto_now=True)

    class Meta:
        db_table="brands"

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)