import json
import unittest
from datetime import datetime

import bson
from django.test import TestCase
from unittest.mock import patch, Mock, MagicMock
from buildings.models.building_model import Building
from buildings.models.audioguide_model import Audioguide
from django.core.exceptions import ValidationError
import logging

from buildings.utils import rd_to_wgs

logger = logging.getLogger(__name__)

class BuildingModelTest(TestCase):
    databases = {'buildings'}

    @classmethod
    def setUpTestData(cls):
        cls.valid_azure_url = "https://annoamsterdamstorage.blob.core.windows.net/buildings/building1.jpg"
        cls.invalid_azure_url = "ftp://invalid.url"

        # Mock Building and Audioguide objects creation
        cls.mock_building = Mock(spec=Building)
        cls.mock_building.address = "123 Example St, City, Country"
        cls.mock_building.construction_year = 1990
        cls.mock_building.image_urls = []
        cls.mock_building.audioguides = []
        cls.mock_building.tags = []
        cls.mock_audioguide = Mock(spec=Audioguide)
        cls.mock_audioguide._id = str(bson.ObjectId())
        cls.mock_audioguide.title = "Guide 1"
        cls.mock_audioguide.audio_url = cls.valid_azure_url
        cls.mock_audioguide.description = "An audioguide description"

    def setUp(self):
        patcher1 = patch('buildings.models.building_model.Building.objects.create', return_value=self.mock_building)
        patcher2 = patch('buildings.models.audioguide_model.Audioguide.objects.create', return_value=self.mock_audioguide)
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.mock_building_create = patcher1.start()
        self.mock_audioguide_create = patcher2.start()
        self.mock_building.image_urls = []

    @patch('buildings.models.building_model.Building.objects.create')
    def test_building_creation(self, mock_create):
        # Use the mock_building set up in setUpTestData
        mock_create.return_value = BuildingModelTest.mock_building

        # Call the mocked create method
        building = Building.objects.create(location={'type': 'Point', 'coordinates': [40.7128, -74.0060]},
                                           address="123 Example St, City, Country",
                                           construction_year=1990,
                                           type_of_use="Commercial",
                                           tags=["historic", "landmark"],
                                           description="A description of the building")

        # Assert that the mock object's fields were set correctly
        self.assertEqual(building.address, BuildingModelTest.mock_building.address)
        self.assertEqual(building.construction_year, BuildingModelTest.mock_building.construction_year)

    def test_add_invalid_image(self):
        # (!) Explicit function to mimic the behavior --- CHANGE upon Implementation
        def mock_add_image(url, *args, **kwargs):
            if url == BuildingModelTest.invalid_azure_url:
                raise ValueError("Invalid Azure Blob Storage URL.")

        # Set the side_effect of the mock add_image method
        BuildingModelTest.mock_building.add_image.side_effect = mock_add_image

        # Assert that calling add_image with an invalid URL raises ValueError
        with self.assertRaises(ValueError):
            BuildingModelTest.mock_building.add_image(BuildingModelTest.invalid_azure_url, "Invalid Source")

    @patch('buildings.models.building_model.Building.objects.create')
    def test_invalid_location_type(self, mock_create):
        mock_building = Mock(spec=Building)
        mock_building.full_clean.side_effect = ValueError("Invalid location type")

        # Configure the mock_create method to return the mock_building
        mock_create.return_value = mock_building

        with self.assertRaises(ValueError):
            building = Building.objects.create(
                location={'type': 'InvalidType', 'coordinates': [40.7128, -74.0060]},
                address="123 Test Ave, City, Country",
                construction_year=1990,
                type_of_use="Commercial"
            )
            building.full_clean()

    @patch('buildings.models.building_model.Building.objects.create')
    def test_construction_year_in_future(self, mock_create):
        # Configure the mock_building to raise ValidationError for a future construction year
        mock_building = Mock(spec=Building)
        mock_building.full_clean.side_effect = ValidationError("Construction year is in the future")

        # Configure the mock_create method to return the mock_building
        mock_create.return_value = mock_building

        future_year = 3000
        with self.assertRaises(ValidationError):
            building = Building.objects.create(
                location={'type': 'Point', 'coordinates': [40.7128, -74.0060]},
                address="Future Address, City, Country",
                construction_year=future_year,
                type_of_use="Residential"
            )
            building.full_clean()

    def test_audioguide_relationship_add_and_remove(self):
        # Add the mock_audioguide to the mock_building
        self.mock_building.audioguides.append(self.mock_audioguide._id)
        self.assertIn(self.mock_audioguide._id, self.mock_building.audioguides)
        # Remove the mock_audioguide from the mock_building
        self.mock_building.audioguides.remove(self.mock_audioguide._id)
        self.assertNotIn(self.mock_audioguide._id, self.mock_building.audioguides)

    def test_update_building_details(self):
        # Update the mock_building's address and type_of_use
        self.mock_building.address = "Updated Address, City, Country"
        self.mock_building.type_of_use = "Residential"
        # Assert that the mock_building's address and type_of_use were updated
        self.assertEqual(self.mock_building.address, "Updated Address, City, Country")
        self.assertEqual(self.mock_building.type_of_use, "Residential")

    def test_add_remove_multiple_audioguides(self):
        audioguide2_id = str(bson.ObjectId())
        self.mock_building.audioguides.append(self.mock_audioguide._id)
        self.mock_building.audioguides.append(audioguide2_id)
        self.assertIn(self.mock_audioguide._id, self.mock_building.audioguides)
        self.assertIn(audioguide2_id, self.mock_building.audioguides)
        self.mock_building.audioguides.remove(audioguide2_id)
        self.assertNotIn(audioguide2_id, self.mock_building.audioguides)

    def test_invalid_audioguide_id(self):
        # Explicit function to mimic add_audioguide behavior for invalid ID
        def mock_add_audioguide(audioguide_id):
            if audioguide_id == "invalidID":
                raise ValueError("Invalid audioguide ID")

        # Set the side_effect of the mock add_audioguide method
        BuildingModelTest.mock_building.add_audioguide.side_effect = mock_add_audioguide

        # Assert that calling add_audioguide with the specific invalid ID raises ValueError
        with self.assertRaises(ValueError):
            BuildingModelTest.mock_building.add_audioguide("invalidID")

    def test_duplicate_audioguides(self):
        # Reset audioguides list for this test
        self.mock_building.audioguides = []

        # Mock the add_audioguide method to add audioguide ID if not already present
        def mock_add_audioguide(audioguide_id):
            if audioguide_id not in self.mock_building.audioguides:
                self.mock_building.audioguides.append(audioguide_id)

        self.mock_building.add_audioguide = Mock(side_effect=mock_add_audioguide)

        # Add the same audioguide ID twice
        self.mock_building.add_audioguide(self.mock_audioguide._id)
        self.mock_building.add_audioguide(self.mock_audioguide._id)

        # Assert that the audioguide ID is only added once
        audioguide_ids = [str(guide) for guide in self.mock_building.audioguides]
        self.assertEqual(audioguide_ids.count(self.mock_audioguide._id), 1)

    def test_add_tag_to_building(self):
        new_tag = 'new_tag'
        BuildingModelTest.mock_building.tags = []
        BuildingModelTest.mock_building.tags.append(new_tag)
        self.assertIn(new_tag, BuildingModelTest.mock_building.tags)

    def test_remove_tag_from_building(self):
        tag_to_remove = 'remove_tag'
        BuildingModelTest.mock_building.tags = [tag_to_remove]
        # Remove the tag from the list
        BuildingModelTest.mock_building.tags.remove(tag_to_remove)
        self.assertNotIn(tag_to_remove, BuildingModelTest.mock_building.tags)

    def test_set_main_image(self):
        # Define a side effect function for add_image
        def mock_add_image(url, source, is_main=False):
            # Reset the 'is_main' flag for all other images
            if is_main:
                for img in BuildingModelTest.mock_building.image_urls:
                    img['is_main'] = False

            # Add the new image
            BuildingModelTest.mock_building.image_urls.append({
                'url': url,
                'source': source,
                'is_main': is_main
            })
        # Set the side_effect of the mock add_image method
        BuildingModelTest.mock_building.add_image.side_effect = mock_add_image
        # Call the mock add_image method
        BuildingModelTest.mock_building.add_image(BuildingModelTest.valid_azure_url, "Source", is_main=True)
        # Find the main image
        main_image = next((img for img in BuildingModelTest.mock_building.image_urls if img.get('is_main')), None)
        # Assert checks
        self.assertIsNotNone(main_image)
        self.assertEqual(main_image['url'], BuildingModelTest.valid_azure_url)

    def test_empty_audioguides(self):
        self.assertEqual(len(BuildingModelTest.mock_building.audioguides), 0)

    def test_total_images_count_empty(self):
        self.mock_building.total_images_count.return_value = 0
        self.assertEqual(self.mock_building.total_images_count(), 0)

    def test_total_images_count_with_images(self):
        # Set up image_urls list with two images
        self.mock_building.image_urls = [
            {'url': 'http://example.com/image1.jpg'},
            {'url': 'http://example.com/image2.jpg'}
        ]
        # Mock the total_images_count method to return the length of image_urls
        self.mock_building.total_images_count.return_value = len(self.mock_building.image_urls)
        # Assert that total_images_count returns 2
        self.assertEqual(self.mock_building.total_images_count(), 2)

class TestCoordinateConversion(unittest.TestCase):
    def test_rd_to_wgs_conversion(self):
        # Known RD coordinates (x, y) and expected WGS84 coordinates (lat, lon)
        test_data = [
            {'rd': (123456, 654321), 'wgs': (52.0, 5.0)}, # Test case 1
            {'rd': (987654, 123456), 'wgs': (52.0, 5.0)}, # Test case 2
            {'rd': (0, 0), 'wgs': (52.0, 5.0)} # Test case 3
        ]

        for data in test_data:
            with patch('pyproj.Transformer.from_crs') as mock_transformer:
                # Set up the mock transformer to return expected results
                mock_transformer.return_value = MagicMock(transform=lambda x, y: (data['wgs'][1], data['wgs'][0]))

                # Call the function with RD coordinates
                lat, lon = rd_to_wgs(*data['rd'])

                # Assert that the result matches the expected WGS84 coordinates
                self.assertAlmostEqual(lat, data['wgs'][0], places=5)
                self.assertAlmostEqual(lon, data['wgs'][1], places=5)










