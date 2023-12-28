from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from .models.building_model import Building
from .models.audioguide_model import Audioguide

import logging

logger = logging.getLogger(__name__)
class BuildingModelTest(TestCase):
    databases = {'buildings'}

    def setUp(self):
        # Set up data for the whole TestCase
        self.building = Building.objects.create(
            preview_image_url="https://example.blob.core.windows.net/buildings/building1.jpg",
            location={'type': 'Point', 'coordinates': [40.7128, -74.0060]},  # Latitude, Longitude
            address="123 Example St, City, Country",
            construction_year=1990,
            type_of_use="Commercial",
            tags=["historic", "landmark"],
            description="A description of the building",
        )
        self.audioguide = Audioguide.objects.create(
            title="Guide 1",
            audio_url="https://example.blob.core.windows.net/audioguides/guide1.mp3",
            description="An audioguide description"
        )

    def test_building_creation(self):
        # Test that a Building instance can be created and its fields are correctly set
        self.assertEqual(self.building.address, "123 Example St, City, Country")
        self.assertEqual(self.building.construction_year, 1990)

    def test_add_image(self):
        # Test the add_image method
        self.building.add_image("https://example.blob.core.windows.net/buildings/building1_img1.jpg", "Source 1")
        self.assertEqual(len(self.building.image_urls), 1)
        self.assertEqual(self.building.image_urls[0]['source'], "Source 1")

    def test_custom_save_method(self):
        # Test the custom save method, particularly the validation of location
        self.assertEqual(self.building.location, {'type': 'Point', 'coordinates': [40.7128, -74.0060]})

    def test_invalid_location_type(self):
        with self.assertRaises(ValueError):
            Building.objects.create(
                location={'type': 'InvalidType', 'coordinates': [40.7128, -74.0060]},
                address="123 Test Ave, City, Country",
                construction_year=1990,
                type_of_use="Commercial"
            )

    def test_construction_year_in_future(self):
        future_year = 3000  # Arbitrary future year
        with self.assertRaises(ValueError):
            Building.objects.create(
                construction_year=future_year,
                address="Future Address",
                type_of_use="Residential"
            )

    def test_invalid_preview_image_url(self):
        building = Building(
            preview_image_url="ftp://invalid.url",  # Intentionally invalid
            location={'type': 'Point', 'coordinates': [40.7128, -74.0060]},
            address="123 Test Ave, City, Country",
            construction_year=1990,
            type_of_use="Commercial"
        )
        with self.assertRaises(ValidationError):
            building.full_clean()  # This should trigger the ValidationError This should trigger the ValidationError

    def test_audioguide_relationship(self):
        # Test adding an audioguide
        self.building.add_audioguide(str(self.audioguide._id))
        self.building.save()

        # Re-fetch the building to ensure the data is up-to-date after addition
        building_after_add = Building.objects.get(_id=self.building._id)
        self.assertIn(str(self.audioguide._id), building_after_add.audioguides)

        # Test removing an audioguide
        building_after_add.remove_audioguide(self.audioguide._id)
        building_after_add.save()

        # Re-fetch the building to ensure the data is up-to-date after removal
        building_after_remove = Building.objects.get(_id=self.building._id)
        if str(self.audioguide._id) in building_after_remove.audioguides:
            logger.error(f"Audioguide {_id} was not removed. Current audioguides: {building_after_remove.audioguides}")
        self.assertNotIn(str(self.audioguide._id), building_after_remove.audioguides)

    def test_update_building_details(self):
        # Update fields
        self.building.address = "Updated Address, City, Country"
        self.building.type_of_use = "Residential"
        self.building.save()

        # Fetch the updated building
        updated_building = Building.objects.get(_id=self.building._id)
        self.assertEqual(updated_building.address, "Updated Address, City, Country")
        self.assertEqual(updated_building.type_of_use, "Residential")

    def test_add_remove_multiple_audioguides(self):
        # Create additional audioguides
        audioguide2 = Audioguide.objects.create(
            title="Guide 2",
            audio_url="https://example.blob.core.windows.net/audioguides/guide2.mp3",
            description="Second audioguide description"
        )

        # Add multiple audioguides
        self.building.add_audioguide(str(self.audioguide._id))
        self.building.add_audioguide(str(audioguide2._id))
        self.building.save()

        # Check they're both added
        building_with_guides = Building.objects.get(_id=self.building._id)
        self.assertIn(str(self.audioguide._id), building_with_guides.audioguides)
        self.assertIn(str(audioguide2._id), building_with_guides.audioguides)

        # Remove one audioguide
        building_with_guides.remove_audioguide(audioguide2._id)
        building_with_guides.save()

        # Check the correct one is removed
        building_after_removal = Building.objects.get(_id=self.building._id)
        self.assertIn(str(self.audioguide._id), building_after_removal.audioguides)
        self.assertNotIn(str(audioguide2._id), building_after_removal.audioguides)

        # Cleanup
        audioguide2.delete()

    def test_invalid_audioguide_id(self):
        invalid_id = "invalidid123"
        with self.assertRaises(ValueError):
            self.building.add_audioguide(invalid_id)

    def test_duplicate_audioguides(self):
        # Add the same audioguide twice
        self.building.add_audioguide(str(self.audioguide._id))
        self.building.add_audioguide(str(self.audioguide._id))
        self.building.save()

        # Check for duplicates
        building_with_duplicates = Building.objects.get(_id=self.building._id)
        self.assertEqual(building_with_duplicates.audioguides.count(str(self.audioguide._id)), 1)

    def tearDown(self):
        # Clean up code for each test
        self.building.delete()
        self.audioguide.delete()
