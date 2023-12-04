
from django.db import models
from buildings.models.timestamp_model import TimeStampedModel

class Audioguide(TimeStampedModel):
    # Fields for the Audioguide model
    title = models.CharField(max_length=255)
    audio_url = models.URLField()
    description = models.TextField()

    def __str__(self):
        return self.title
