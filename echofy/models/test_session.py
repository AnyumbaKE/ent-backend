from django.db import models
from django.conf import settings  # This refers to AUTH_USER_MODEL
from django.utils.timezone import now

class TestSession(models.Model):
    MODE_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES)
    started_at = models.DateTimeField(default=now)
    correct_no = models.PositiveIntegerField(default=0)
    closed = models.BooleanField(default=False)

    def is_expired(self):
        from datetime import timedelta
        return now() > self.started_at + timedelta(minutes=5)

    def mark_closed_if_expired(self):
        if self.is_expired():
            self.closed = True
            self.save()
            return True
        return False
