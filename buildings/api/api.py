import logging

from bson import ObjectId as BsonObjectId, ObjectId
from django.http import Http404
from djongo.models import ObjectIdField
from rest_framework import serializers, viewsets
import bson

from buildings.models.audioguide_model import Audioguide
from buildings.models.building_model import Building


# Set up logging
logger = logging.getLogger(__name__)

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = '__all__'

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