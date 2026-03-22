from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        SALES = 'SALES', 'Sales Team'
        ACCOUNTS = 'ACCOUNTS', 'Accounts Team'
        TRACKING = 'TRACKING', 'Tracking Team'
        CHA = 'CHA', 'CHA'
        FORWARDER = 'FORWARDER', 'Forwarder'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.SALES)
    phone = models.CharField(max_length=15, blank=True)
    branches = models.ManyToManyField('masters.Branch', blank=True, related_name='users')

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
