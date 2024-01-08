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
        # Valid and invalid URLs for testing
        self.valid_azure_url = "https://annoamsterdamstorage.blob.core.windows.net/profile-pictures/building1.jpg"
        self.invalid_azure_url = "ftp://invalid.url"

        # Setting up a Building instance
        self.building = Building.objects.create(
            location={'type': 'Point', 'coordinates': [40.7128, -74.0060]},  # Latitude, Longitude
            address="123 Example St, City, Country",
            construction_year=1990,
            type_of_use="Commercial",
            tags=["historic", "landmark"],
            description="A description of the building",
        )

        # Setting up an Audioguide instance
        self.audioguide = Audioguide.objects.create(
            title="Guide 1",
            audio_url=self.valid_azure_url,  # Using a valid URL
            description="An audioguide description"
        )

    def test_building_creation(self):
        self.assertEqual(self.building.address, "123 Example St, City, Country")
        self.assertEqual(self.building.construction_year, 1990)

    def test_add_valid_image(self):
        # Testing adding a valid image URL
        try:
            self.building.add_image(self.valid_azure_url, "Source 1", year=2020, is_main=True)
            self.assertEqual(len(self.building.image_urls), 1)
            self.assertTrue(self.building.image_urls[0]['is_main'])
        except ValidationError:
            self.fail("add_image unexpectedly raised ValidationError for a valid URL!")

    def test_add_invalid_image(self):
        # Test adding an invalid image URL
        with self.assertRaises(ValueError) as context:
            self.building.add_image(self.invalid_azure_url, "Invalid Source")

        # Check that the error message is as expected
        self.assertTrue('Invalid Azure Blob Storage URL' in str(context.exception))

    def test_invalid_location_type(self):
        with self.assertRaises(ValueError):
            Building.objects.create(
                location={'type': 'InvalidType', 'coordinates': [40.7128, -74.0060]},
                address="123 Test Ave, City, Country",
                construction_year=1990,
                type_of_use="Commercial"
            )

    def test_construction_year_in_future(self):
        future_year = 3000
        with self.assertRaises(ValueError):
            Building.objects.create(
                construction_year=future_year,
                address="Future Address",
                type_of_use="Residential"
            )

    def test_audioguide_relationship(self):
        self.building.add_audioguide(str(self.audioguide._id))
        self.building.save()

        building_after_add = Building.objects.get(_id=self.building._id)
        self.assertIn(str(self.audioguide._id), building_after_add.audioguides)

        building_after_add.remove_audioguide(self.audioguide._id)
        building_after_add.save()

        building_after_remove = Building.objects.get(_id=self.building._id)
        self.assertNotIn(str(self.audioguide._id), building_after_remove.audioguides)

    def test_update_building_details(self):
        self.building.address = "Updated Address, City, Country"
        self.building.type_of_use = "Residential"
        self.building.save()

        updated_building = Building.objects.get(_id=self.building._id)
        self.assertEqual(updated_building.address, "Updated Address, City, Country")
        self.assertEqual(updated_building.type_of_use, "Residential")

    def test_add_remove_multiple_audioguides(self):
        audioguide2 = Audioguide.objects.create(
            title="Guide 2",
            audio_url=self.valid_azure_url,
            description="Second audioguide description"
        )

        self.building.add_audioguide(str(self.audioguide._id))
        self.building.add_audioguide(str(audioguide2._id))
        self.building.save()

        building_with_guides = Building.objects.get(_id=self.building._id)
        self.assertIn(str(self.audioguide._id), building_with_guides.audioguides)
        self.assertIn(str(audioguide2._id), building_with_guides.audioguides)

        building_with_guides.remove_audioguide(audioguide2._id)
        building_with_guides.save()

        building_after_removal = Building.objects.get(_id=self.building._id)
        self.assertNotIn(str(audioguide2._id), building_after_removal.audioguides)

        audioguide2.delete()

    def test_invalid_audioguide_id(self):
        invalid_id = "invalidid123"
        with self.assertRaises(ValueError):
            self.building.add_audioguide(invalid_id)

    def test_duplicate_audioguides(self):
        self.building.add_audioguide(str(self.audioguide._id))
        self.building.add_audioguide(str(self.audioguide._id))
        self.building.save()

        building_with_duplicates = Building.objects.get(_id=self.building._id)
        audioguide_ids = [str(guide) for guide in building_with_duplicates.audioguides]
        self.assertEqual(audioguide_ids.count(str(self.audioguide._id)), 1)

    def tearDown(self):
        self.building.delete()
        self.audioguide.delete()
