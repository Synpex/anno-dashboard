from django.test import TestCase
from django.contrib.auth.models import User
from .models.profile_model import UserProfile  # Ensure this is the correct import path

class UserProfileModelTest(TestCase):

    def setUp(self):
        # Create a user for the profile
        # Assume that a UserProfile is created automatically upon user creation
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.get(user=self.user)  # Retrieve the automatically created profile

    def test_profile_creation(self):
        # Test that a UserProfile is created automatically when a new User is created
        self.assertIsNotNone(self.profile, "UserProfile should be created automatically when a new User is created.")
        self.assertEqual(self.user.profile, self.profile, "The created profile should be linked to the user.")

    def test_profile_fields(self):
        # Test the fields of the created UserProfile
        # Check if picture is empty, which is the expected default state
        self.assertFalse(self.profile.picture, "Profile picture should be None by default.")
        # As telephone can be null, it should be None by default if not set
        self.assertIsNone(self.profile.telephone, "Telephone should be None by default.")

    def test_update_profile(self):
        # Test updating the UserProfile
        new_telephone = '1234567890'
        self.profile.telephone = new_telephone
        self.profile.save()

        # Retrieve the profile again to ensure it's updated
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.telephone, new_telephone, "The profile's telephone should be updated.")

    def tearDown(self):
        # Clean up after each test case.
        # Deleting the user should also delete the associated UserProfile due to the CASCADE delete
        self.user.delete()
