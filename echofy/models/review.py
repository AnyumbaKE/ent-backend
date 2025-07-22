from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ReviewModel(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_reviews')
    title = models.CharField(max_length=255)
    text = models.TextField()
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')

    def __str__(self):
        return f"From {self.sender} to {self.receiver}: {self.title}"
