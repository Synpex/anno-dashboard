from django.db import models

class TempImage(models.Model):
    session_key = models.CharField(max_length=40)  # The session key of the user who uploaded the image
    image = models.ImageField(upload_to='temp/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['session_key']),  # Index for faster lookups by session_key
        ]
