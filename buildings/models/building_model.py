import uuid

from django.db import models
from django.core.validators import URLValidator

# Import Local models
from buildings.models.timestamp_model import TimeStampedModel
from buildings.models.audioguide_model import Audioguide

class Building(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    preview_image_url = models.CharField(
        max_length=1024,
        validators=[URLValidator()],
        help_text="URL to a preview image of the building."
    )
    latitude = models.FloatField(
        help_text="Geographic latitude of the building's location."
    )
    longitude = models.FloatField(
        help_text="Geographic longitude of the building's location."
    )
    address = models.CharField(
        max_length=255,
        help_text="Physical address of the building."
    )
    construction_year = models.IntegerField(
        help_text="Year when the building was constructed."
    )
    type_of_use = models.CharField(
        max_length=100,
        help_text="The intended use of the building (e.g., residential, commercial)."
    )
    tags = models.JSONField(
        help_text="JSON-formatted list of tags related to the building."
    )
    description = models.TextField(
        help_text="Detailed description of the building."
    )
    image_urls = models.JSONField(
        help_text="JSON-formatted list of URLs to images of the building."
    )
    timeline = models.JSONField(
        help_text="JSON-formatted data representing key events in the building's history."
    )
    audioguides = models.ManyToManyField(
        Audioguide,
        blank=True,
        help_text="Associated audio guides for the building."
    )

    def __str__(self):
        return self.address
