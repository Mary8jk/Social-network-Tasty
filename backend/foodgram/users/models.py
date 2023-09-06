from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Почта',
        max_length=60,
        unique=True,
        blank=False)
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=50,
        blank=False)
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=50,
        blank=False)

    def __str__(self):
        return self.username
