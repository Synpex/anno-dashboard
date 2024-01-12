import json
import logging
import os
import re

from azure.storage.blob import BlobServiceClient
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from pymongo import MongoClient
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
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
from django.views.decorators.http import require_http_methods, require_POST
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_search_params(request):
    if request.method == 'POST':
        # Retrieve existing data or initialize if not present
        search_params = request.session.get('search_params', {})
        selected_building = request.session.get('selected_building', {})

        # Extract new data from request
        new_search_params = request.data.get('search_params')
        initial_selected_building = request.data.get('selected_building')

        # Validate the necessary data is provided
        if new_search_params is None or initial_selected_building is None:
            missing_params = []
            if new_search_params is None:
                missing_params.append("search_params")
            if initial_selected_building is None:
                missing_params.append("selected_building")
            return Response({
                'status': 'error',
                'message': 'Missing necessary data.',
                'missing_data': missing_params
            }, status=400)

        # Update existing data with new data
        search_params.update(new_search_params)
        selected_building.update(initial_selected_building)

        # Save updated data back to session
        request.session['search_params'] = search_params
        request.session['selected_building'] = selected_building

        # Explicitly mark the session as modified to ensure it's saved
        request.session.modified = True

        # Return a success response
        return Response({
            'status': 'success',
            'data': {
                'search_params': search_params,
                'selected_building': selected_building
            }
        })

    return Response({'status': 'error', 'message': 'Invalid request method. This endpoint supports POST only.'},
                    status=405)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_building_details(request):
    logger.info("Received data: %s", request.data)
    if request.method == 'POST':
        # Retrieve existing selected building data or initialize if not present
        selected_building = request.session.get('selected_building', {})

        # Extract new data from request
        new_selected_building = request.data.get('new_selected_building', {})

        # Directly update the selected_building dictionary with the new data
        selected_building.update(new_selected_building)

        # Log the updates for confirmation
        logger.info("Updated selected_building with new data: %s", selected_building)

        # Save updated data back to session
        request.session['selected_building'] = selected_building

        # Explicitly mark the session as modified to ensure it's saved
        request.session.modified = True

        # Return a success response
        return Response({'status': 'success', 'data': {'selected_building': selected_building}})

    return Response({'status': 'error', 'message': 'Invalid request method. This endpoint supports POST only.'}, status=405)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_temp_images(request):
    if request.method == 'POST':
        logger.debug(f"Received request to upload images: {request.FILES}")
        logger.debug(f"Received request to upload metadata: {request.POST}")

        try:
            images_metadata = []
            user_id = request.user.id
            session_id = request.session.session_key

            temp_folder_path = os.path.join(settings.MEDIA_ROOT, f'temp/user_{user_id}_{session_id}')
            os.makedirs(temp_folder_path, exist_ok=True)

            # Retrieve the set of uploaded images from the session, converting it from a list to a set
            uploaded_images = set(request.session.get('uploaded_images', []))

            fs = FileSystemStorage(location=temp_folder_path)

            for key in request.FILES:
                if key.startswith('image_'):
                    index = key.split('_')[1]
                    image = request.FILES[key]
                    new_filename = f"{user_id}_{session_id}_{image.name}"

                    if new_filename in uploaded_images:
                        logger.info(f"Skipping already uploaded image: {new_filename}")
                        continue

                    uploaded_images.add(new_filename)
                    metadata_key = f'metadata_{index}'

                    if metadata_key in request.POST:
                        meta = json.loads(request.POST[metadata_key])
                        filename = fs.save(new_filename, image)
                        image_path = fs.url(filename)

                        image_meta = {
                            'file_path': image_path,
                            'source': meta.get('source', ''),
                            'year': meta.get('year', ''),
                            'is_preview': meta.get('is_preview', False),
                            'user_id': user_id,
                        }
                        images_metadata.append(image_meta)
                    else:
                        logger.error(f"No metadata found for image key: {key}")

            # Convert the set back to a list before storing it in the session
            request.session['uploaded_images'] = list(uploaded_images)
            request.session['images_metadata'] = images_metadata
            request.session.modified = True

            return JsonResponse({'status': 'success', 'data': images_metadata})

        except Exception as e:
            logger.error(f"Error in processing images: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method. This endpoint supports POST only.'}, status=405)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@login_required
def remove_image_from_session(request):
    if request.method == 'POST':
        try:
            index = request.data.get('index', None)
            user_id = request.user.id  # Assuming you have access to the user ID here
            session_key = request.session.session_key  # Get the session key

            if index is not None and 'images_metadata' in request.session:
                images_metadata = request.session['images_metadata']
                if 0 <= index < len(images_metadata):
                    # Construct the path to the user's temp folder
                    user_folder = os.path.join(settings.MEDIA_ROOT, 'temp', f'user_{user_id}_{session_key}')
                    file_path = images_metadata[index]['file_path']
                    full_path = os.path.join(user_folder, file_path.lstrip('/'))

                    logger.debug(f"Attempting to remove image at index {index}: {full_path}")

                    # Remove the image metadata from the session
                    images_metadata.pop(index)
                    request.session['images_metadata'] = images_metadata
                    request.session.modified = True

                    # Attempt to delete the file from the filesystem
                    if os.path.exists(full_path):
                        os.remove(full_path)
                        logger.info(f"Successfully removed file: {full_path}")

                        # Check if the folder is now empty, and if so, delete it
                        if not os.listdir(user_folder):
                            os.rmdir(user_folder)
                            logger.info(f"Removed empty folder: {user_folder}")

                        return JsonResponse({'status': 'success', 'message': 'Image and file removed'})

                    else:
                        logger.warning(f"File not found for removal: {full_path}")
                        return JsonResponse({'status': 'warning', 'message': 'Image metadata removed, but file was not found'})
                else:
                    logger.error(f"Invalid index provided for removal: {index}")
                    return JsonResponse({'status': 'error', 'message': 'Invalid index'}, status=400)
            else:
                logger.error("No index provided or no images in session for removal.")
                return JsonResponse({'status': 'error', 'message': 'Index not provided or no images in session'}, status=400)
        except Exception as e:
            logger.error(f"Error in removing image from session: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method. This endpoint supports POST only.'}, status=405)
class BuildingByYearList(generics.ListAPIView):
    serializer_class = BuildingSerializer

    def get_queryset(self):
        """
        This view should return a list of all buildings for
        the construction year as determined by the year portion of the URL.
        """
        year = self.kwargs['year']
        return Building.objects.filter(construction_year=year)


@login_required
@require_POST
def update_timeline(request):
    try:
        # Decode JSON from the request body
        data = json.loads(request.body)
        timeline_data = data.get('timeline', [])

        # Log the received data
        logger.debug(f"Received timeline data: {timeline_data}")

        # Update the session with the new timeline data
        request.session['timeline'] = timeline_data
        request.session.modified = True

        return JsonResponse({'status': 'success', 'message': 'Timeline updated successfully'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_POST
def publish_building(request):
    if request.method == 'POST':
        # Azure Storage settings
        account_name = settings.AZURE_ACCOUNT_NAME
        account_key = settings.AZURE_ACCOUNT_KEY
        container_name = "buildings"

        logger.info("Connecting to Azure Blob Storage")
        blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net",
                                                credential=account_key)

        # Directory where images are stored on your server
        local_images_directory = f'{settings.MEDIA_ROOT}/temp/user_{request.user.id}_{request.session.session_key}'

        # Get images metadata from the session
        images_metadata = request.session.get('images_metadata', [])
        image_urls = []

        # Upload each image to Azure Blob Storage and transform image data
        for image_meta in images_metadata:
            local_image_path = os.path.join(local_images_directory, image_meta['file_path'])
            if os.path.exists(local_image_path):
                with open(local_image_path, 'rb') as image_file:
                    blob_client = blob_service_client.get_blob_client(container=container_name,
                                                                      blob=image_meta['file_path'])
                    blob_client.upload_blob(image_file, overwrite=True)
                    logger.info(f"Uploaded image {image_meta['file_path']} to Azure Blob Storage")

                image_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{image_meta['file_path']}"
                image_urls.append({
                    'url': image_url,
                    'source': image_meta.get('source', ''),
                    'year': image_meta.get('year', ''),
                    'is_main': image_meta.get('is_preview', False)
                })

                os.remove(local_image_path)
                logger.info(f"Deleted local image file {local_image_path}")

        # Transform selected_building data
        selected_building = request.session.get('selected_building', {})
        coordinates = selected_building.get('coordinates')
        if not coordinates or len(coordinates) != 2:
            logger.error("Invalid or missing coordinates in selected_building.")
            return JsonResponse({'error': 'Invalid or missing coordinates'}, status=400)

        building, created = Building.objects.get_or_create(
            _id=selected_building.get('_id')
        )
        logger.info(f"{'Created' if created else 'Updated'} building record with ID: {building._id}")

        building.name = selected_building.get('alternative_name', '') if selected_building.get('alternative_name',
                                                                                               '') else building.name
        building.address = f"{selected_building.get('address', '')}, {selected_building.get('city', '')}, {selected_building.get('postcode', '')}"
        building.construction_year = selected_building.get('constructionYear', building.construction_year)
        building.type_of_use = selected_building.get('typeOfUse', building.type_of_use)
        building.tags = selected_building.get('tags', building.tags)
        building.location = {"type": "Point", "coordinates": coordinates}
        building.image_urls = image_urls
        building.description = selected_building.get('description', building.description)

        try:
            building.save()
            logger.info(f"Saved building data for {_id}")
        except Exception as e:
            logger.error(f"Error saving building data: {e}")
            return JsonResponse({'error': 'Error saving building data'}, status=500)

        return JsonResponse({'status': 'success', 'building_id': str(building._id)})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

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
            openapi.Parameter('lat', openapi.IN_QUERY, description="Latitude of the location.", type=openapi.TYPE_NUMBER),
            openapi.Parameter('lon', openapi.IN_QUERY, description="Longitude of the location", type=openapi.TYPE_NUMBER),
            openapi.Parameter('century', openapi.IN_QUERY, description="Century of the building's construction (e.g., 20 for 20th Century).", type=openapi.TYPE_INTEGER),
            openapi.Parameter('address_or_name', openapi.IN_QUERY, description="Partial or full address or name of the building to search for.", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request, *args, **kwargs):
        logger.debug("Received request for SortedBuildingsView.")
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        century = request.query_params.get('century')
        address_or_name = request.query_params.get('address_or_name')

        if lat and lon:
            return self.get_buildings_by_coordinates(lat, lon, century, address_or_name)
        elif century:
            return self.get_buildings_by_century(century, address_or_name)
        else:
            return self.get_all_buildings(address_or_name)

    def get_buildings_by_coordinates(self, lat, lon, century, address_or_name):
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
                        'key': 'location.coordinates', #2dsphereIndex
                        'maxDistance': 500
                    }
                },
                {'$match': {'active': True}}
            ]

            # Add regex search if address_or_name is provided
            if address_or_name:
                regex_pattern = re.compile(f".*{re.escape(address_or_name)}.*", re.IGNORECASE)
                pipeline.append({'$match': {'$or': [{'address': regex_pattern}, {'name': regex_pattern}]}})

            if century and century.isdigit():
                century = int(century)
                start_year = (century - 1) * 100 + 1
                end_year = century * 100
                pipeline.append({'$match': {'construction_year': {'$gte': start_year, '$lt': end_year}}})

            pipeline.extend([
                {'$limit': 10},
                {'$addFields': {'distanceRounded': {'$round': [{'$ifNull': ['$distance', 0]}, 2]}}},
                {'$project': {'_id': 1, 'image_urls':1, 'distanceRounded': 1, 'location': 1, 'address': 1,
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

    def get_buildings_by_century(self, century, address_or_name):
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

        # Add regex search if address_or_name is provided
        if address_or_name:
            regex_pattern = re.compile(f".*{re.escape(address_or_name)}.*", re.IGNORECASE)
            query['$or'] = [{'address': regex_pattern}, {'name': regex_pattern}]

        projection = {
            '_id': 1,
            'name': 1,
            'location': 1,
            'address': 1,
            'construction_year': 1,
            'type_of_use': 1,
            'image_urls': 1
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

    def get_all_buildings(self, address_name_filter):
        logger.debug("No coordinates or century provided, retrieving all active buildings using PyMongo.")
        try:
            client = MongoClient(os.getenv('MONGO_DB_CONNECTION_STRING'))
            db = client[os.getenv('MONGO_DB_NAME')]
            collection = db[Building._meta.db_table]

            query = {"active": True}
            if address_name_filter:
                regex_pattern = re.compile(f".*{re.escape(address_name_filter)}.*", re.IGNORECASE)
                query['$or'] = [{'address': regex_pattern}, {'name': regex_pattern}]

            projection = {
                '_id': 1,
                'name': 1,
                'location': 1,
                'address': 1,
                'construction_year': 1,
                'type_of_use': 1,
                'image_urls': 1
            }

            buildings_cursor = collection.find(query, projection).limit(10)
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



