# Import necessary Django modules and validators
from django.db import models
from djongo.models import ObjectIdField

from Core.fields import MongoObjectIdField
from buildings.models.timestamp_model import TimeStampedModel  # Importing the base model with timestamps
from Core.validators import validate_azure_blob_url  # Importing the custom Azure URL validator

class Audioguide(TimeStampedModel):
    """
    The Audioguide model represents an audio guide associated with a building. It inherits from TimeStampedModel,
    which provides it with fields for tracking creation and modification times, as well as the creator.
    """
    _id = ObjectIdField()

    # title: A string field for the title of the audioguide. Max length is set to 255 characters.
    title = models.CharField(max_length=255, help_text="Title of the audioguide.")

    # audio_url: A URL field for the location of the audio file. It's validated using the custom Azure Blob URL validator.
    # The validator ensures that the URL is a valid Azure Blob Storage URL, which is where the audio files are stored.
    audio_url = models.URLField(validators=[validate_azure_blob_url], help_text="URL to the audio file stored in Azure Blob Storage.")

    # description: A text field for a detailed description of the audioguide. This field can hold an unlimited number of characters.
    description = models.TextField(help_text="Detailed description of the audioguide.")

    def __str__(self):
        """
        The __str__ method returns a human-readable representation of the Audioguide object.
        In this case, it returns the title of the audioguide.
        """
        return self.title
