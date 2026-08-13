from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):

    def create_user(
        self,
        email=None,
        password=None,
        **extra_fields
    ):

        if not email and not extra_fields.get("mobile_number"):
            raise ValueError(
                "Email or mobile number is required."
            )

        if email:
            email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        email,
        password=None,
        **extra_fields
    ):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault(
            "role",
            self.model.Role.ADMIN
        )
        extra_fields.setdefault(
            "is_email_verified",
            True
        )
        extra_fields.setdefault(
            "is_deleted",
            False
        )

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser must have is_staff=True."
            )

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must have is_superuser=True."
            )

        if not password:
            raise ValueError(
                "Superuser must have a password."
            )

        return self.create_user(
            email=email,
            password=password,
            username="admin",
            **extra_fields
        )