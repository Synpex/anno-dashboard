import json
import logging

from bson import ObjectId as BsonObjectId, ObjectId
from django.http import Http404
from rest_framework import serializers, viewsets
import bson


from buildings.fields import GeoPointField
from buildings.models.audioguide_model import Audioguide
from buildings.models.building_model import Building


# Set up logging
logger = logging.getLogger(__name__)

class ObjectIdField(serializers.Field):
    """A custom field to use for the ObjectId type."""
    def to_representation(self, value):
        if isinstance(value, dict):  # Handle the case where value is a dictionary
            return str(value.get('_id'))
        return str(value)

class BuildingSerializer(serializers.ModelSerializer):
    location = GeoPointField()
    class Meta:
        model = Building
        fields = '__all__'



class SlimBuildingSerializer(serializers.ModelSerializer):# Custom field for handling MongoDB's ObjectId
    distance = serializers.FloatField(source='distanceRounded', read_only=True)  # FloatField for distance
    _id = ObjectIdField(read_only=True)  # Custom field for handling MongoDB's ObjectId
    location = GeoPointField(read_only=True)
    name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    main_image_url = serializers.SerializerMethodField()
    class Meta:
        model = Building
        fields = ('_id', 'name', 'location', 'distance', 'main_image_url', 'address', 'construction_year', 'type_of_use', 'active')

    def get_main_image_url(self, obj):
        image_urls_str = obj.get('image_urls', '[]')
        try:
            image_urls = json.loads(image_urls_str)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode image_urls: {image_urls_str}")
            return None

        for img in image_urls:
            if img.get('is_main', False):
                return img.get('url')
        return None


class BuildingViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing buildings.
    """
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    lookup_field = 'id'

    def get_object(self):
        """
        Override to handle MongoDB ObjectId.
        """
        # Retrieve the ID from the URL
        obj_id = self.kwargs.get(self.lookup_field)
        logger.info(f"Attempting to retrieve object with ID: {obj_id}")

        try:
            # Convert the ID to a valid ObjectId
            obj_id = BsonObjectId(obj_id)
            logger.info(f"Converted string ID to ObjectId: {obj_id}")
        except Exception as e:
            logger.error(f"Error converting ID to ObjectId: {e}")
            raise Http404("Invalid ObjectId format.")

        # Retrieve the object using the converted ObjectId
        try:
            obj = self.queryset.get(_id=obj_id)
            logger.info(f"Object found: {obj}")
            return obj
        except Building.DoesNotExist:
            logger.warning(f"No Building found with ID: {obj_id}")
            raise Http404("No Building matches the given query.")
        except Exception as e:
            logger.error(f"Error retrieving object: {e}")
            raise Http404("An error occurred while retrieving the Building.")


class AudioguideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audioguide
        fields = '__all__'
class AudioguideViewSet(viewsets.ModelViewSet):
    queryset = Audioguide.objects.all()
    serializer_class = AudioguideSerializer
    lookup_field = "id"

    def get_queryset(self):
        """
        Optionally restricts the returned audioguides,
        by filtering against a `query` parameter in the URL.
        """
        queryset = Audioguide.objects.all()
        query = self.request.query_params.get('query', None)
        if query is not None:
            queryset = queryset.filter(title__icontains=query)
        return queryset

    def get_object(self):
        """
        Override to handle MongoDB ObjectId.
        """
        # Retrieve the ID from the URL
        obj_id = self.kwargs.get(self.lookup_field)
        logger.info(f"Attempting to retrieve object with ID: {obj_id}")

        try:
            # Convert the ID to a valid ObjectId
            obj_id = BsonObjectId(obj_id)
            logger.info(f"Converted string ID to ObjectId: {obj_id}")
        except Exception as e:
            logger.error(f"Error converting ID to ObjectId: {e}")
            raise Http404("Invalid ObjectId format.")

        # Retrieve the object using the converted ObjectId
        try:
            obj = self.queryset.get(_id=obj_id)
            logger.info(f"Object found: {obj}")
            return obj
        except Building.DoesNotExist:
            logger.warning(f"No Audioguide found with ID: {obj_id}")
            raise Http404("No Audioguide matches the given query.")
        except Exception as e:
            logger.error(f"Error retrieving object: {e}")
            raise Http404("An error occurred while retrieving the Audioguide.")