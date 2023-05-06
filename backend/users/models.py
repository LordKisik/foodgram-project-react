from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(Enum):
    USER = 'Пользователь'
    ADMIN = 'Администратор'


class User(AbstractUser):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=150, unique=True)
    password = models.CharField(max_length=254)
    role = models.CharField(
        max_length=20,
        choices=[(role.value, role.name) for role in UserRole],
        default=UserRole.USER.value)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username', 'password']

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN or self.is_superuser
