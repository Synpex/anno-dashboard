import bson
from bson import ObjectId as BsonObjectId
from django.db import models
from django.core.validators import URLValidator
from djongo.models.fields import ObjectIdField

from buildings.fields import CustomJSONField
from buildings.models.timestamp_model import TimeStampedModel  # Base model with timestamps
from Core.validators import validate_azure_blob_url, validate_timeline  # Custom validators

class Building(TimeStampedModel):
    """
    The Building model represents a physical building. It includes information about the building's location,
    appearance, usage, and history. This model inherits from TimeStampedModel, which provides it with fields
    for tracking creation and modification times, as well as the creator.
    """
    _id = ObjectIdField()  # Use the custom field for the primary key

    # preview_image_url: A URL pointing to an image of the building. It's validated to ensure it's a well-formed URL and
    # matches the expected Azure Blob Storage URL pattern.
    preview_image_url = models.CharField(
        max_length=1024,
        validators=[URLValidator(), validate_azure_blob_url],
        help_text="URL to a preview image of the building."
    )

    # location: A Custom JSON field storing the geographic location of the building as a GeoJSON point. This allows for
    # efficient geospatial queries within Cosmos DB.
    location = CustomJSONField(
        help_text="GeoJSON formatted point data representing the building's location."
    )

    # address: A string field storing the physical address of the building.
    address = models.CharField(
        max_length=255,
        help_text="Physical address of the building."
    )

    # construction_year: An integer field representing the year the building was constructed.
    construction_year = models.IntegerField(
        help_text="Year when the building was constructed."
    )

    # type_of_use: A string field describing the intended use of the building (e.g., residential, commercial).
    type_of_use = models.CharField(
        max_length=100,
        help_text="The intended use of the building (e.g., residential, commercial)."
    )

    # tags: A JSON field storing a list of tags related to the building. This allows for flexible tagging as new
    # tags can be added without altering the database schema.
    tags = models.JSONField(
        help_text="JSON-formatted list of tags related to the building."
    )

    # description: A text field storing a detailed description of the building.
    description = models.TextField(
        help_text="Detailed description of the building."
    )

    # image_urls: A JSON field storing a list of objects, each containing a URL to an image of the building and its source.
    # This allows for storing multiple images and corresponding sources.
    image_urls = models.JSONField(
        help_text="JSON-formatted list of objects with URLs to images of the building and their sources.",
        default=list  # Ensures the default is an empty list
    )

    # timeline: A JSON field storing a list of significant historical events related to the building. Each event has a
    # year and a description. Custom validation ensures the correct format for each entry.
    timeline = models.JSONField(
        help_text="JSON-formatted data representing key events in the building's history.",
        validators = [validate_timeline],
        default = list  # Ensures the default is an empty list
    )

    # active: A boolean field indicating whether the building is active or not.
    active = models.BooleanField(
        default=True,  # Set the default value to True (active)
        help_text="Indicates whether the building is active or not."
    )

    # audioguides: A JSON field storing a list of embedded audioguide details. Each entry contains the ID of the audioguide
    audioguides = models.JSONField(
        help_text="JSON-formatted list of audioguides.",
        default=list  # Default to an empty list
    )

    # Used to access the id of the building in Django Templates
    @property
    def public_id(self):
        return self._id

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to ensure that the location field
        is stored as a proper GeoJSON object in the database.
        """
        # Convert location from string to dictionary if necessary
        global json
        if isinstance(self.location, str):
            try:
                # Attempt to convert the string to a dictionary
                import json
                self.location = json.loads(self.location)
            except json.JSONDecodeError:
                # If conversion fails, raise an error
                raise ValueError("Location must be a valid GeoJSON point")

        # Validate the location field
        if self.location is None or 'type' not in self.location or self.location['type'] != 'Point':
            raise ValueError("Location must be a GeoJSON point")

        # Call the parent class's save method with all arguments
        super().save(*args, **kwargs)

    def add_image(self, image_url, source):
        """
        Method to add an image and its source to the building. This allows for dynamic addition of images
        without needing to directly manipulate the image_urls field.
        """
        self.image_urls.append({'url': image_url, 'source': source})
        self.save()


    def century(self):
        """
        Determines the century in which the building was constructed.
        Returns:
            int: The century of the construction year.
        """
        if self.construction_year:
            return (self.construction_year - 1) // 100 + 1
        return None


    def add_audioguide(self, audioguide_id):
        """
        Add an audioguide ID to the building.
        """
        try:
            # Ensure the ID is a valid ObjectId
            valid_id = BsonObjectId(str(audioguide_id))
        except bson.errors.InvalidId:
            raise ValueError(f"Invalid audioguide ID: {audioguide_id}")

        # Convert to string if it's an ObjectId
        if isinstance(valid_id, BsonObjectId):
            audioguide_id = str(valid_id)

        if audioguide_id not in self.audioguides:
            self.audioguides.append(audioguide_id)
            self.save()


    def remove_audioguide(self, audioguide_id):
        """
        Remove an audioguide ID from the building.
        """
        try:
            self.audioguides.remove(str(audioguide_id))
            self.save()
        except ValueError:
            pass  # Handle the case where the audioguide_id is not in the list

    def total_images_count(self):
        count = len(self.image_urls)
        if self.preview_image_url:
            count += 1
        return count

    def __str__(self):
        """
        The __str__ method returns a human-readable representation of the Building object.
        In this case, it returns the address of the building.
        """
        return self.address
