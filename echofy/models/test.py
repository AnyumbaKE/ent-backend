from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class TestModel(models.Model):
    LEVEL_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('fr', 'French'),
        ('sw', 'Swahili'),
        ('de', 'German'),
        ('ar', 'Arabic'),
        # Add more as needed
    ]

    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tests')

    type = models.CharField(max_length=50)
    question = models.TextField()
    audio = models.CharField(max_length=255)
    correctAnswer = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.question} ({self.level} - {self.language})"
