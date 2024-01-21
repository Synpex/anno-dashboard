"""
from storages.backends.azure_storage import AzureStorage

class BuildingStorage(AzureStorage):
    azure_container = 'buildings'
    expiration_secs = None

class AudioguideStorage(AzureStorage):
    azure_container = 'audioguides'
    expiration_secs = None"
"""