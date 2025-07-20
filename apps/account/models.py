from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin


# Create your models here.

class Account(AbstractUser, ):

    email = models.EmailField(unique=True, max_length=255)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
