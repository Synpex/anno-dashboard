# Custom validator for Azure Blob URLs
import re

from django.core.exceptions import ValidationError
from django.conf import settings

def validate_azure_blob_url(value):
    # Fetch Azure storage details from settings
    account_name = settings.AZURE_ACCOUNT_NAME
    container_name = "buildings"

    # regular expression pattern for Azure Blob Storage URLs
    pattern = rf'https://{account_name}.blob.core.windows.net/{container_name}/.+'
    if not re.match(pattern, value):
        raise ValidationError("Invalid Azure Blob Storage URL.")

# Custom validator for timeline entries
def validate_timeline(value):
    # Check that value is a list
    if not isinstance(value, list):
        raise ValidationError("Timeline must be a list.")
    for entry in value:
        # Check that each entry is a dictionary with 'year' and 'description' keys
        if not (isinstance(entry, dict) and 'year' in entry and 'description' in entry):
            raise ValidationError("Each timeline entry must be an object with 'year' and 'description'.")