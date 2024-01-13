from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth.models import User
from users.models.profile_model import UserProfile
from users.validators import validate_international_phone_number


class UserProfileModelTest(TestCase):

    def setUp(self):
        # Assuming UserProfile is automatically created when a User is created
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.get(user=self.user)

    def test_profile_creation(self):
        self.assertIsNotNone(self.profile, "UserProfile should be created automatically when a new User is created.")
        self.assertEqual(self.user.profile, self.profile, "The created profile should be linked to the user.")


    def test_profile_fields(self):
        self.assertFalse(self.profile.picture, "Profile picture should be None by default.")
        self.assertIsNone(self.profile.telephone, "Telephone should be None by default.")


    def test_update_profile(self):
        new_telephone = '+436607676007'
        self.profile.telephone = new_telephone
        self.profile.save()
        self.assertEqual(self.profile.telephone, new_telephone, "The profile's telephone should be updated.")


    def test_str_representation(self):
        expected_str = f'{self.user.username} Profile'
        self.assertEqual(str(self.profile), expected_str,
                         "The string representation of the profile should match the expected value.")

    def test_set_telephone_to_none(self):
        self.profile.telephone = '+436607676007'
        self.profile.save()
        self.assertIsNotNone(self.profile.telephone, "Telephone should not be None after setting a valid value.")
        self.profile.telephone = None
        self.profile.save()
        self.assertIsNone(self.profile.telephone, "Telephone should be set to None.")

    def test_update_profile_valid_telephone(self):
        valid_numbers = [
            "+436607676007",  # Valid E.164 format
            "+1 234 567 8900",  # Valid E.164 format with spaces
            "+44 20 1234 5678",  # Valid UK number
            "+81 3 1234 5678",  # Valid Japan number
        ]

        for number in valid_numbers:
            with self.subTest(number=number):
                self.profile.telephone = number
                self.profile.full_clean()
                self.profile.save()
                self.assertEqual(self.profile.telephone, number,
                                 "The profile's telephone should be updated with a valid number.")

    def test_update_profile_invalid_telephone(self):
        invalid_numbers = [
            "+1234567890",  # Missing '+' sign
            "+12345",  # Too short
            "+12345678901234567890",  # Too long
            "+1 123",  # Incomplete number
            "+1 abcdefgh",  # Invalid characters
            "+1 (123) 456-7890",  # Invalid formatting
            "not_a_phone_number",  # Invalid format
        ]

        for number in invalid_numbers:
            with self.subTest(number=number):
                with self.assertRaises(ValidationError):
                    self.profile.telephone = number
                    self.profile.full_clean()  # This will trigger validation
                    self.profile.save()
    def tearDown(self):
        if hasattr(self, 'user'):
            self.user.delete()