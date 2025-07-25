from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('blogger', 'Blogger'),
        ('user', 'user'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    full_name = models.CharField(max_length=100, blank=False)
    email = models.EmailField(unique=True)
    activated = models.BooleanField(default=True)
