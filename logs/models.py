from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

LEVELS = ['CRITICAL', 'DEBUG', 'ERROR', 'WARNING', 'INFO']
ENVIRONMENTS=['development', 'testing', 'production']

User = get_user_model()


def validate_environment(value):
    if value not in ENVIRONMENTS:
        raise ValidationError(
            f'{value} is not a valid environment',
            params={'value': value}
        )


class Agent(models.Model):
    ENV_CHOICES = [(env, env) for env in ENVIRONMENTS]
    environment = models.CharField(
        max_length=20, choices=ENV_CHOICES, validators=[validate_environment]
    )
    name = models.CharField(max_length=256)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    address = models.GenericIPAddressField(null=True)

    def __str__(self):
        return f'{self.name} ({self.environment})'


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
    details = models.TextField()
    datetime = models.DateTimeField(blank=True, null=True)
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    archived = models.BooleanField(default=False)

    @property
    def source(self):
        return self.agent.name if self.agent else None

    @property
    def collected_by(self):
        return str(self.user) if self.user else None

    def __str__(self):
        return f'Event {self.id} - {self.source}'

    class Meta:
        ordering = ['datetime']
