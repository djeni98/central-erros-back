from django.db import models
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator

LEVELS = ['CRITICAL', 'DEBUG', 'ERROR', 'WARNING', 'INFO']

validate_password = MinLengthValidator(8)


class User(models.Model):
    name = models.CharField(max_length=50)
    last_login = models.DateTimeField(null=True)
    email = models.EmailField()
    # Password validation is made in view
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.name or f'User {self.id}'


class UserForm(forms.ModelForm):
    password = forms.CharField(disabled=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'password']


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
