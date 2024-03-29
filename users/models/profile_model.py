from django.db import models
from django.contrib.auth.models import User
from users.validators import validate_international_phone_number

from users.storage_backend import ProfilePictureStorage

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    picture = models.ImageField(
        upload_to='profile_pics',
        storage=ProfilePictureStorage(),
        blank=True,
        null=True,
        default=None,
    )
    telephone = models.CharField(max_length=20, blank=True, null=True, default=None, validators=[validate_international_phone_number])
    def __str__(self):
        return f'{self.user.username} Profile'
