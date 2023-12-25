from django.conf import settings
from django.db import models

class TimeStampedModel(models.Model):
    # Records the exact date and time when this record was first created. Automatically set upon creation and not meant to be modified.
    created_at = models.DateTimeField(auto_now_add=True, help_text="The date and time this record was created. Automatically set upon creation.")

    # Records the last date and time this record was updated. Automatically updated every time the record is saved.
    updated_at = models.DateTimeField(auto_now=True, help_text="The date and time this record was last updated. Automatically updated on save.")
    class Meta:
        abstract = True  # Specifies that this model will not be used to create any database table.
