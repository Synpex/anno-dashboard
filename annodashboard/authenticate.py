# authentication.py

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

class APIKeyAuthentication(BaseAuthentication):

    def authenticate(self, request):
        api_key = request.headers.get('X-API-KEY')
        if api_key and api_key == settings.MY_API_KEY:
            return (None, None)  # Authentication successful
        raise AuthenticationFailed('No API Key provided or invalid key')
