from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator

from django.contrib.auth.base_user import AbstractBaseUser

LEVELS = ['CRITICAL', 'DEBUG', 'ERROR', 'WARNING', 'INFO']

validate_password = MinLengthValidator(8)


class User(AbstractBaseUser):
    name = models.CharField(max_length=300, blank=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.name or self.email


def validate_level(value):
    if value not in LEVELS:
        raise ValidationError(
            f'{value} is not a valid level',
            params={'value': value}
        )


class Event(models.Model):
    LEVEL_CHOICES = [(level, level) for level in LEVELS]
    level = models.CharField(
        max_length=20, choices=LEVEL_CHOICES, validators=[validate_level]
    )

    description = models.TextField()
    source = models.CharField(max_length=256)
    datetime = models.DateTimeField(blank=True)
    # events?
    details = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return f'Event {self.id} - {self.source}'
