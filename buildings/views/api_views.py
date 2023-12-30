import logging
import os

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from pymongo import MongoClient
from rest_framework.response import Response


from rest_framework import generics
from rest_framework.views import APIView

from buildings.models.building_model import Building
from buildings.api.api import BuildingSerializer, SlimBuildingSerializer

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BuildingByYearList(generics.ListAPIView):
    serializer_class = BuildingSerializer

    def get_queryset(self):
        """
        This view should return a list of all buildings for
        the construction year as determined by the year portion of the URL.
        """
        year = self.kwargs['year']
        return Building.objects.filter(construction_year=year)

class BuildingSearchView(APIView):
    """
    API endpoint that allows users to search for buildings by address.
    """
    def get(self, request, *args, **kwargs):
        # Retrieve the address query from the request's query parameters
        query = request.GET.get('address', '')

        if query:
            # Filter buildings where the address contains the query text, case-insensitive
            buildings = Building.objects.filter(address__icontains=query)
        else:
            buildings = Building.objects.none()  # Return no results if no query

        # Serialize and return the buildings
        serializer = SlimBuildingSerializer(buildings, many=True)
        return Response(serializer.data)

class SortedBuildingsView(APIView):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('lat', openapi.IN_QUERY, description="Latitude of the location.", type=openapi.TYPE_NUMBER),
            openapi.Parameter('lon', openapi.IN_QUERY, description="Longitude of the location", type=openapi.TYPE_NUMBER),
            openapi.Parameter('century', openapi.IN_QUERY, description="Century of the building's construction (e.g., 20 for 20th Century).", type=openapi.TYPE_INTEGER)
        ]
    )
    def get(self, request, *args, **kwargs):
        logger.debug("Received request for SortedBuildingsView.")
        # Retrieve the latitude, longitude, and century from the query parameters
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        century = request.query_params.get('century')

        # Validate the latitude and longitude
        try:
            lat = float(lat)
            lon = float(lon)
            logger.debug(f"Converted coordinates - Lat: {lat}, Lon: {lon}")
        except (TypeError, ValueError) as e:
            logger.error(f"Error converting coordinates: {e}")
            return Response({"error": "Invalid latitude or longitude."}, status=400)

        # Ensure the coordinates are within the valid range
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            logger.warning(f"Coordinates out of range - Lat: {lat}, Lon: {lon}")
            return Response({"error": "Latitude must be between -90 and 90 and longitude between -180 and 180."}, status=400)

        client = MongoClient(os.getenv('MONGO_DB_CONNECTION_STRING'))
        db = client[os.getenv('MONGO_DB_NAME')]
        collection = db[Building._meta.db_table]

        # Initialize the pipeline with $geoNear as the first stage
        pipeline = [
            {
                '$geoNear': {
                    'near': {
                        'type': 'Point',
                        'coordinates': [lon, lat]  # User's coordinates
                    },
                    'distanceField': 'distance',
                    'spherical': True,
                    'key': 'location.coordinates'
                }
            }
        ]

        # Conditionally apply the century filter after $geoNear
        if century and century.isdigit():
            century = int(century)
            start_year = (century - 1) * 100 + 1
            end_year = century * 100

            # Add the $match stage to the pipeline for century filtering
            pipeline.append({
                '$match': {
                    'construction_year': {'$gte': start_year, '$lt': end_year}
                }
            })

        # Add additional stages as needed, for example:
        pipeline.append({
            '$addFields': {
                'distanceRounded': {
                    '$round': [
                        {'$ifNull': ['$distance', 0]},
                        2
                    ]
                }
            }
        })

        pipeline.append({'$limit': 10})

        pipeline.append({
            '$project': {
                '_id': 1,  # Include the _id field
                'distanceRounded': 1,
                'preview_image_url': 1,
                'address': 1,
                'construction_year': 1,
                'type_of_use': 1,
                # Add any other fields you want to include in the response
            }
        })

        logger.debug(f"Executing aggregation pipeline: {pipeline}")
        buildings_cursor = collection.aggregate(pipeline)
        buildings_list = list(buildings_cursor)

        # Close the connection to the database
        client.close()

        serializer = SlimBuildingSerializer(buildings_list, many=True)
        logger.debug("Buildings serialized successfully.")

        return Response(serializer.data)