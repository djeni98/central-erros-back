from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator

LEVELS = ['CRITICAL', 'DEBUG', 'ERROR', 'WARNING', 'INFO']

validate_password = MinLengthValidator(8)


class User(models.Model):
    name = models.CharField(max_length=50)
    last_login = models.DateTimeField(blank=True)
    email = models.EmailField()
    password = models.CharField(
        max_length=50, validators=[validate_password]
    )


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
