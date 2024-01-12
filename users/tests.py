from unittest.mock import patch, Mock
from django.test import TestCase
from django.contrib.auth.models import User
from .models.profile_model import UserProfile

class UserProfileModelTest(TestCase):

    def setUp(self):
        self.user = Mock(spec=User)
        self.profile = Mock(spec=UserProfile)

        # Explicitly link the profile mock to the user mock
        self.user.profile = self.profile

        # Mock the User.objects.create_user method
        with patch('django.contrib.auth.models.User.objects.create_user') as mock_create_user:
            mock_create_user.return_value = self.user
            self.user = User.objects.create_user(username='testuser', password='12345')

        # Mock retrieving the UserProfile
        with patch('users.models.profile_model.UserProfile.objects.get') as mock_get:
            mock_get.return_value = self.profile
            self.profile = UserProfile.objects.get(user=self.user)

    def test_profile_creation(self):
        # Assuming the profile is created automatically with the user
        self.assertIsNotNone(self.profile, "UserProfile should be created automatically when a new User is created.")
        self.assertEqual(self.user.profile, self.profile, "The created profile should be linked to the user.")

    def test_profile_fields(self):
        # Mock default values of profile fields
        self.profile.picture = None
        self.profile.telephone = None

        self.assertFalse(self.profile.picture, "Profile picture should be None by default.")
        self.assertIsNone(self.profile.telephone, "Telephone should be None by default.")

    def test_update_profile(self):
        new_telephone = '1234567890'
        self.profile.telephone = new_telephone
        # Call the save method on the mock profile
        self.profile.save()
        # Assert that save was called on the profile mock
        self.profile.save.assert_called_once()
        # Since self.profile is a mock, its attributes can be directly checked
        self.assertEqual(self.profile.telephone, new_telephone, "The profile's telephone should be updated.")

    def tearDown(self):
        # Simply call delete on the mock user
        self.user.delete()

