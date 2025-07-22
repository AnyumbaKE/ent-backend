from django.db import models
from django.conf import settings

class Blog(models.Model):
    APPROVAL_CHOICES = [
        ('pending', 'Awaiting Validation'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    text = models.TextField()
    image_url = models.URLField(blank=True, null=True)  # cloudinary-stored image URL
    created_at = models.DateTimeField(auto_now_add=True)
    approval_status = models.CharField(
        max_length=10,
        choices=APPROVAL_CHOICES,
        default='pending'
    )

    def __str__(self):
        return self.title
