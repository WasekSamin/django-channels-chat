from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from datetime import datetime


class AccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("Email field is required!")
        elif not username:
            raise ValueError("Username field is required!")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, username, password=None):
        if not email:
            raise ValueError("Email field is required!")
        elif not username:
            raise ValueError("Username field is required!")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class Account(AbstractBaseUser):
    username = models.CharField(max_length=120, null=True)
    email = models.EmailField(null=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_online = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=datetime.now)

    objects = AccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def __str__(self):
        return self.email

    