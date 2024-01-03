import json
import logging
import os

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from pymongo import MongoClient
from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework import generics
from rest_framework.views import APIView

from buildings.models.building_model import Building
from buildings.api.api import BuildingSerializer, SlimBuildingSerializer
from buildings.utils import rd_to_wgs

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# views.py
import requests
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.conf import settings


@require_http_methods(["GET"])
def api_proxy_view(request):
    api_key = settings.BAG_API_KEY
    baseURL = settings.BAG_API_BASE_URL
    # Extract the necessary parameters from the request
    postcode = request.GET.get('postcode', '').strip()
    housenumber = request.GET.get('huisnummer', '').strip()
    textual_search = request.GET.get('q', '').strip()  # Getting textual search parameter

    # Determine the type of search to perform based on the provided parameters
    if textual_search and not (postcode or housenumber):
        # Perform textual search
        api_url = f'{baseURL}/adressenuitgebreid?q={textual_search}'
    elif postcode and housenumber and not textual_search:
        # Perform search by postcode and housenumber
        api_url = f'{baseURL}/adressenuitgebreid?postcode={postcode}&huisnummer={housenumber}'
    else:
        # If neither or both types of search data are provided, return a bad request
        return HttpResponseBadRequest('Provide either a textual search or both postcode and housenumber.')
    # Required Headers for Kadaster API
    headers = {
        'Accept-Crs': 'epsg:28992',  # Coordinate Reference System
        'Accept': 'application/hal+json',  # Response format
        'Content-Type': 'application/json',
        'X-API-KEY': api_key
    }

    # Make the request to the external API
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        try:
            data = response.json()
            if '_embedded' in data and 'adressen' in data['_embedded']:
                for adres in data['_embedded']['adressen']:
                    geom = adres.get('adresseerbaarObjectGeometrie')
                    if geom:
                        # Check if it's a point
                        if 'punt' in geom:
                            coords = geom['punt']['coordinates']
                            lat, lon = rd_to_wgs(coords[0], coords[1])
                            adres['adresseerbaarObjectGeometrie']['punt']['coordinates'] = [lon, lat]

                        # Check if it's a polygon ('vlak')
                        elif 'vlak' in geom and geom['vlak']['type'] == 'Polygon':
                            # Extract the first point of the polygon
                            first_point = geom['vlak']['coordinates'][0][0]
                            lat, lon = rd_to_wgs(first_point[0], first_point[1])
                            # Replace the polygon with a point in the response
                            adres['adresseerbaarObjectGeometrie'] = {
                                'punt': {
                                    'type': 'Point',
                                    'coordinates': [lon, lat]
                                }
                            }

            return JsonResponse(data, safe=False)
        except ValueError:
            return HttpResponseBadRequest('Invalid JSON received from the external API')
    else:
        return HttpResponseBadRequest(f'Status {response.status_code}: {response.text}')

@csrf_exempt
@api_view(['POST'])
def save_selected_building(request):
    # Ensure the request is a POST request
    if request.method == 'POST':
        # DRF's request.data will give you the parsed data
        data = request.data
        request.session['selected_building'] = data  # Save data in session
        print(request.session['selected_building'])
        return Response({'status': 'success'})

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

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='address', in_=openapi.IN_QUERY,
                description="Partial or full address to search for",
                type=openapi.TYPE_STRING
            )
        ]
    )
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
            openapi.Parameter('lat', openapi.IN_QUERY, description="Latitude of the location.",
                              type=openapi.TYPE_NUMBER),
            openapi.Parameter('lon', openapi.IN_QUERY, description="Longitude of the location",
                              type=openapi.TYPE_NUMBER),
            openapi.Parameter('century', openapi.IN_QUERY,
                              description="Century of the building's construction (e.g., 20 for 20th Century).",
                              type=openapi.TYPE_INTEGER)
        ]
    )
    def get(self, request, *args, **kwargs):
        logger.debug("Received request for SortedBuildingsView.")
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        century = request.query_params.get('century')

        if lat and lon:
            return self.get_buildings_by_coordinates(lat, lon, century)
        elif century:
            return self.get_buildings_by_century(century)
        else:
            return self.get_all_buildings()

    def get_buildings_by_coordinates(self, lat, lon, century):
        try:
            lat = float(lat)
            lon = float(lon)
            logger.debug(f"Converted coordinates - Lat: {lat}, Lon: {lon}")

            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                logger.warning(f"Coordinates out of range - Lat: {lat}, Lon: {lon}")
                return Response({"error": "Latitude must be between -90 and 90 and longitude between -180 and 180."},
                                status=400)

            client = MongoClient(os.getenv('MONGO_DB_CONNECTION_STRING'))
            db = client[os.getenv('MONGO_DB_NAME')]
            collection = db[Building._meta.db_table]

            pipeline = [
                {
                    '$geoNear': {
                        'near': {'type': 'Point', 'coordinates': [lon, lat]},
                        'distanceField': 'distance',
                        'spherical': True,
                        'key': 'location.coordinates' #2dsphereIndex
                    }
                },
                {'$match': {'active': True}}
            ]

            if century and century.isdigit():
                century = int(century)
                start_year = (century - 1) * 100 + 1
                end_year = century * 100
                pipeline.append({'$match': {'construction_year': {'$gte': start_year, '$lt': end_year}}})

            pipeline.extend([
                {'$limit': 10},
                {'$addFields': {'distanceRounded': {'$round': [{'$ifNull': ['$distance', 0]}, 2]}}},
                {'$project': {'_id': 1, 'distanceRounded': 1, 'location': 1, 'preview_image_url': 1, 'address': 1,
                              'construction_year': 1, 'type_of_use': 1}}
            ])

            logger.debug(f"Executing aggregation pipeline: {pipeline}")
            buildings_cursor = collection.aggregate(pipeline)
            buildings_list = list(buildings_cursor)
            client.close()

        except (TypeError, ValueError) as e:
            logger.error(f"Error converting coordinates: {e}")
            return Response({"error": "Invalid latitude or longitude."}, status=400)

        serializer = SlimBuildingSerializer(buildings_list, many=True)
        logger.debug("Buildings serialized successfully.")
        return Response(serializer.data)

    def get_buildings_by_century(self, century):
        logger.debug("No coordinates provided, using plain MongoDB querying.")
        client = MongoClient(os.getenv('MONGO_DB_CONNECTION_STRING'))
        db = client[os.getenv('MONGO_DB_NAME')]
        collection = db[Building._meta.db_table]

        query = {'active': True}
        if century and century.isdigit():
            century = int(century)
            start_year = (century - 1) * 100 + 1
            end_year = century * 100
            logger.debug(f"Filtering by century: {century} (Years: {start_year}-{end_year})")
            query['construction_year'] = {'$gte': start_year, '$lt': end_year}

        projection = {
            '_id': 1,
            'location': 1,
            'preview_image_url': 1,
            'address': 1,
            'construction_year': 1,
            'type_of_use': 1
        }

        try:
            buildings_cursor = collection.find(query, projection).limit(10)
            buildings_list = list(buildings_cursor)
            logger.debug(f"Retrieved {len(buildings_list)} buildings from MongoDB.")
        except Exception as e:
            logger.error(f"Error querying MongoDB: {e}")
            return Response({"error": "Error querying MongoDB."}, status=500)
        finally:
            client.close()

        serializer = SlimBuildingSerializer(buildings_list, many=True)
        logger.debug("Buildings serialized successfully.")
        return Response(serializer.data)

    def get_all_buildings(self):
        logger.debug("No coordinates or century provided, retrieving all active buildings using PyMongo.")
        try:
            # Establish a connection to the MongoDB server
            client = MongoClient(os.getenv('MONGO_DB_CONNECTION_STRING'))
            db = client[os.getenv('MONGO_DB_NAME')]
            collection = db[Building._meta.db_table]

            # Query for all active buildings
            query = {"active": True}
            projection = {
                '_id': 1,
                'location': 1,
                'preview_image_url': 1,
                'address': 1,
                'construction_year': 1,
                'type_of_use': 1
            }
            buildings_cursor = collection.find(query, projection).limit(10)  # Adjust limit as needed
            buildings_list = list(buildings_cursor)

            logger.debug(f"Retrieved {len(buildings_list)} buildings from MongoDB.")

        except Exception as e:
            logger.error(f"Error querying MongoDB: {e}", exc_info=True)
            return Response({"error": "Error querying MongoDB."}, status=500)
        finally:
            client.close()

        serializer = SlimBuildingSerializer(buildings_list, many=True)
        logger.debug("Buildings serialized successfully.")
        return Response(serializer.data)

