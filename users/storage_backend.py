from storages.backends.azure_storage import AzureStorage

class ProfilePictureStorage(AzureStorage):
    azure_container = 'profile-pictures'
    expiration_secs = None