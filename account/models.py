import datetime
from django.db import models

# Create your models here.
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone
from django.core.validators import FileExtensionValidator

from django.utils.translation import gettext_lazy as _
from account.countryapi import CountryChoiceField
from report.models import validate_image_size


class Category(models.Model):
    name = models.CharField(max_length=100)

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ("admin", "Admin"),
        ("contributor", "Contributor"),
        ("user", "User"),
        ("guest", "Guest"),
    )
    selected_categories = models.ManyToManyField(Category, blank=True, related_name='users')
    username = models.CharField(max_length=150, unique=True, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=ROLES, default="guest")
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    why_here = models.CharField(max_length=400, default="", blank=False)
    country = models.CharField(max_length=100, choices=CountryChoiceField().get_country_choices())

    # country = CountryChoiceField(
    #     max_length=100, choices=CountryChoiceField().get_country_choices()
    # )
    is_active = models.BooleanField(default=True)

    birth_date = models.DateField(
        blank=False, null=False, default=datetime.date(1900, 1, 1)
    )

    profile_picture = models.ImageField(
        upload_to="profile_pics/", blank=True, null=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png"]), validate_image_size]
    )
    objects = UserManager()


    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
        # required fields to createsuperuser account
    REQUIRED_FIELDS = ["email", "password", "role"]

    def __str__(self):
        return self.username
