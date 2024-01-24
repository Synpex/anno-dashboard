import json
import logging
import os
import re

from azure.storage.blob import BlobServiceClient
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from urllib.parse import quote
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from pymongo import MongoClient
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from bson import ObjectId as BsonObjectId

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
    user_id = request.user.id if request.user.is_authenticated else 'Anonymous'

    try:
        # Existing code for API key, base URL, and parameter retrieval
        api_key = settings.BAG_API_KEY
        baseURL = settings.BAG_API_BASE_URL
        postcode = request.GET.get('postcode', '').strip()
        housenumber = request.GET.get('huisnummer', '').strip()
        textual_search = request.GET.get('q', '').strip()

        # Build the API URL based on the provided parameters
        if textual_search and not (postcode or housenumber):
            api_url = f'{baseURL}/adressenuitgebreid?q={textual_search}'
        elif postcode and housenumber and not textual_search:
            api_url = f'{baseURL}/adressenuitgebreid?postcode={postcode}&huisnummer={housenumber}'
        else:
            logger.error(f"User ID {user_id}: Invalid request parameters received.")
            messages.error(request, 'Invalid request parameters received.')
            return HttpResponseBadRequest('Provide either a textual search or both postcode and housenumber.')

        # Set the request headers
        headers = {
            'Accept-Crs': 'epsg:28992',
            'Accept': 'application/hal+json',
            'Content-Type': 'application/json',
            'X-API-KEY': api_key
        }

        # Make the API request
        response = requests.get(api_url, headers=headers)
        logger.info(f"User ID {user_id}: API request to {api_url} returned status code {response.status_code}")

        # Handle the response
        if response.status_code == 200:
            data = response.json()
            # Process the response and convert coordinates
            if '_embedded' in data and 'adressen' in data['_embedded']:
                for adres in data['_embedded']['adressen']:
                    geom = adres.get('adresseerbaarObjectGeometrie')
                    if geom:
                        if 'punt' in geom:
                            coords = geom['punt']['coordinates']
                            lat, lon = rd_to_wgs(coords[0], coords[1])
                            adres['adresseerbaarObjectGeometrie']['punt']['coordinates'] = [lon, lat]
                        elif 'vlak' in geom and geom['vlak']['type'] == 'Polygon':
                            first_point = geom['vlak']['coordinates'][0][0]
                            lat, lon = rd_to_wgs(first_point[0], first_point[1])
                            adres['adresseerbaarObjectGeometrie'] = {'punt': {'type': 'Point', 'coordinates': [lon, lat]}}

            messages.success(request, 'Request processed successfully.')
            return JsonResponse(data, safe=False)
        else:
            error_msg = f'Status {response.status_code}: {response.text}'
            logger.error(f"User ID {user_id}: Error from external API: {error_msg}")
            messages.error(request, f'Error processing request: {error_msg}')
            return HttpResponseBadRequest(error_msg)

    except ValueError as e:
        error_msg = f'Invalid JSON received from the external API: {e}'
        logger.error(f"User ID {user_id}: ValueError in processing response: {error_msg}")
        messages.error(request, error_msg)
        return HttpResponseBadRequest(error_msg)
    except Exception as e:
        error_msg = f'An error occurred while processing the request: {e}'
        logger.error(f"User ID {user_id}: Error in api_proxy_view: {error_msg}")
        messages.error(request, error_msg)
        return HttpResponseBadRequest(error_msg)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(auto_schema=None)
def update_search_params(request):
    user_id = request.user.id  # Get the user ID from the request
    logger.info(f"User {user_id} initiated search parameters update.")

    if request.method == 'POST':
        try:
            logger.debug(f"Received search parameters update from user {user_id}: {request.data}")

            search_params = request.session.get('search_params', {})
            selected_building = request.session.get('selected_building', {})

            new_search_params = request.data.get('search_params')
            initial_selected_building = request.data.get('selected_building')

            if new_search_params is None or initial_selected_building is None:
                missing_params = []
                if new_search_params is None:
                    missing_params.append("search_params")
                if initial_selected_building is None:
                    missing_params.append("selected_building")

                logger.warning(f"User {user_id} did not provide necessary data for search parameters update.")
                return Response({
                    'status': 'error',
                    'message': 'Missing necessary data.',
                    'missing_data': missing_params
                }, status=400)

            search_params.update(new_search_params)
            selected_building.update(initial_selected_building)

            request.session['search_params'] = search_params
            request.session['selected_building'] = selected_building
            request.session.modified = True

            logger.info(f"User {user_id} successfully updated search parameters and selected building in session.")
            return Response({
                'status': 'success',
                'data': {
                    'search_params': search_params,
                    'selected_building': selected_building
                }
            })

        except Exception as e:
            logger.error(f"User {user_id} encountered an error in updating search parameters: {e}", exc_info=True)
            return Response({'status': 'error', 'message': str(e)}, status=500)

    logger.warning(f"User {user_id} made an invalid request method to update search parameters.")
    return Response({'status': 'error', 'message': 'Invalid request method. This endpoint supports POST only.'}, status=405)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(auto_schema=None)
def update_building_details(request):
    user_id = request.user.id  # Get the user ID from the request
    logger.info(f"User {user_id} initiated building details update.")

    if request.method == 'POST':
        try:
            logger.debug(f"Received building update data from user {user_id}: {request.data}")

            selected_building = request.session.get('selected_building', {})
            new_selected_building = request.data.get('new_selected_building', {})

            if not new_selected_building:
                messages.error(request, 'No new building details provided.')
                return Response({'status': 'error', 'message': 'No new building details provided.'}, status=400)

            selected_building.update(new_selected_building)
            request.session['selected_building'] = selected_building
            request.session.modified = True

            messages.success(request, 'Building details updated successfully.')
            logger.info(f"User {user_id} successfully updated building details in session.")
            return Response({'status': 'success', 'data': {'selected_building': selected_building}})

        except Exception as e:
            messages.error(request, 'An error occurred while updating building details.')
            logger.error(f"User {user_id} encountered an error in updating building details: {e}", exc_info=True)
            return Response({'status': 'error', 'message': str(e)}, status=500)

    messages.error(request, 'Invalid request method. This endpoint supports POST only.')
    logger.warning(f"User {user_id} made an invalid request method to update building details.")
    return Response({'status': 'error', 'message': 'Invalid request method. This endpoint supports POST only.'}, status=405)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(auto_schema=None)
def upload_temp_images(request):
    user_id = request.user.id
    session_key = request.session.session_key

    logger.info(f"User {user_id} initiated image upload.")
    if request.method == 'POST':
        try:
            logger.debug(f"Received request to upload images: {request.FILES}")
            logger.debug(f"Received request to upload metadata: {request.POST}")

            temp_folder_path = os.path.join(settings.MEDIA_ROOT, f'temp/user_{user_id}_{session_key}')
            os.makedirs(temp_folder_path, exist_ok=True)

            uploaded_images = set(request.session.get('uploaded_images', []))
            images_metadata = []

            fs = FileSystemStorage(location=temp_folder_path)

            for key in request.FILES:
                if key.startswith('image_'):
                    index = key.split('_')[1]
                    image = request.FILES[key]
                    new_filename = f"{user_id}_{session_key}_{image.name}"

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
                        logger.error(f"User {user_id} provided image without metadata: {key}")

            request.session['uploaded_images'] = list(uploaded_images)
            request.session['images_metadata'] = images_metadata
            request.session.modified = True

            messages.success(request, 'Images uploaded successfully.')
            logger.info(f"User {user_id} successfully uploaded images. Metadata updated in session.")

            return JsonResponse({'status': 'success', 'data': images_metadata})

        except Exception as e:
            messages.error(request, 'An error occurred while processing images.')
            logger.error(f"User {user_id} encountered an error in processing images: {e}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    messages.error(request, 'Invalid request method. This endpoint supports POST only.')
    logger.warning(f"User {user_id} made an invalid request method to upload images.")
    return JsonResponse({'status': 'error', 'message': 'Invalid request method. This endpoint supports POST only.'}, status=405)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@login_required
@swagger_auto_schema(auto_schema=None)
def remove_image_from_session(request):
    user_id = request.user.id
    session_key = request.session.session_key

    logger.info(f"User {user_id} initiated image removal from session.")

    if request.method == 'POST':
        try:
            index = request.data.get('index', None)

            if index is not None and 'images_metadata' in request.session:
                images_metadata = request.session['images_metadata']

                if 0 <= index < len(images_metadata):
                    user_folder = os.path.join(settings.MEDIA_ROOT, 'temp', f'user_{user_id}_{session_key}')
                    file_path = images_metadata[index]['file_path']
                    full_path = os.path.join(user_folder, file_path.lstrip('/'))

                    logger.debug(f"User {user_id} is removing image at index {index}: {full_path}")

                    images_metadata.pop(index)
                    request.session['images_metadata'] = images_metadata
                    request.session.modified = True

                    if os.path.exists(full_path):
                        os.remove(full_path)
                        logger.info(f"User {user_id} removed file: {full_path}")

                        if not os.listdir(user_folder):
                            os.rmdir(user_folder)
                            logger.info(f"User {user_id} removed empty folder: {user_folder}")

                        messages.success(request, 'Image and file removed successfully.')
                        return JsonResponse({'status': 'success', 'message': 'Image and file removed'})

                    else:
                        logger.warning(f"User {user_id} could not find file for removal: {full_path}")
                        messages.warning(request, 'Image metadata removed, but file was not found.')
                        return JsonResponse({'status': 'warning', 'message': 'Image metadata removed, but file was not found'})
                else:
                    logger.error(f"User {user_id} provided invalid index for image removal: {index}")
                    messages.error(request, 'Invalid index provided for image removal.')
                    return JsonResponse({'status': 'error', 'message': 'Invalid index'}, status=400)
            else:
                logger.error(f"User {user_id} attempted to remove an image without providing an index or with no images in session.")
                messages.error(request, 'Index not provided or no images in session.')
                return JsonResponse({'status': 'error', 'message': 'Index not provided or no images in session'}, status=400)
        except Exception as e:
            logger.error(f"User {user_id} encountered an error in removing image from session: {e}", exc_info=True)
            messages.error(request, 'An error occurred while removing the image from the session.')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        logger.warning(f"User {user_id} made an invalid request method to remove image from session.")
        messages.error(request, 'Invalid request method. This endpoint supports POST only.')
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_building_session_data(request):
    user_id = request.user.id
    logger.info(f"User {user_id} initiated clearing building session data.")

    try:
        # List of session keys related to buildings that need to be cleared
        building_session_keys = ['selected_building', 'images_metadata', 'timeline', 'uploaded_images', 'search_params']

        # Clear each key from the session if it exists
        for key in building_session_keys:
            if key in request.session:
                del request.session[key]

        # Mark the session as modified to save changes
        request.session.modified = True

        logger.info(f"User {user_id} successfully cleared building session data.")
        return JsonResponse({'status': 'success', 'message': 'Building session data cleared successfully'})

    except Exception as e:
        logger.error(f"User {user_id} encountered an error in clearing building session data: {e}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_POST
@swagger_auto_schema(auto_schema=None)
def update_timeline(request):
    user_id = request.user.id

    # Retrieve building address from session, if available
    building_address = request.session.get('selected_building', {}).get('address', 'Unknown address')

    logger.info(f"User {user_id} is updating the timeline for building at {building_address}.")

    try:
        # Decode JSON from the request body
        data = json.loads(request.body)
        timeline_data = data.get('timeline', [])

        # Log the received data
        logger.debug(f"User {user_id} received timeline data for {building_address}: {timeline_data}")

        # Validate timeline_data structure if needed
        # Example validation logic can be added here

        # Update the session with the new timeline data
        request.session['timeline'] = timeline_data
        request.session.modified = True

        messages.success(request, 'Timeline updated successfully.')
        logger.info(f"User {user_id} successfully updated the timeline for {building_address}.")
        return JsonResponse({'status': 'success', 'message': 'Timeline updated successfully'})

    except json.JSONDecodeError as e:
        messages.error(request, 'Error updating timeline: Invalid JSON provided.')
        logger.error(f"User {user_id} provided invalid JSON for {building_address}: {e}")
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    except Exception as e:
        messages.error(request, 'Error updating timeline.')
        logger.error(f"User {user_id} encountered an error while updating timeline for {building_address}: {e}",
                     exc_info=True)
        return JsonResponse({'status': 'error', 'message': 'Error updating timeline'}, status=500)


@login_required
@require_POST
@swagger_auto_schema(auto_schema=None)
def publish_building(request):
    user_id = request.user.id
    logger.info(f"User {user_id} initiated the building publication process.")

    try:
        # Azure Storage settings
        account_name = settings.AZURE_ACCOUNT_NAME
        account_key = settings.AZURE_ACCOUNT_KEY
        container_name = "buildings"
        blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net", credential=account_key)
        # Retrieve the selected building data from the session
        selected_building = request.session.get('selected_building', {})
        building_address = selected_building.get('address', '')
        if not building_address:
            logger.error(f"User {user_id}: Building address is missing.")
            return JsonResponse({'error': 'Building address is missing'}, status=400)
        # Create a folder name for the building based on the address
        azure_folder_name = quote(building_address.replace(' ', '_').lower())
        local_images_directory = f'{settings.MEDIA_ROOT}/temp/user_{user_id}_{request.session.session_key}'
        images_metadata = request.session.get('images_metadata', [])
        image_urls = []
        # Upload the images to Azure Blob Storage
        for image_meta in images_metadata:
            relative_image_path = image_meta['file_path'].lstrip('/')
            local_image_path = os.path.join(local_images_directory, relative_image_path)
            if os.path.exists(local_image_path):
                try:
                    with open(local_image_path, 'rb') as image_file:
                        blob_path = f"{azure_folder_name}/{relative_image_path}"
                        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)
                        blob_client.upload_blob(image_file, overwrite=True)
                        logger.info(f"User {user_id}: Uploaded image {blob_path} to Azure Blob Storage")
                    # Construct the URL to the uploaded image
                    image_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_path}"
                    image_urls.append({
                        'url': image_url,
                        'source': image_meta.get('source', ''),
                        'year': image_meta.get('year', ''),
                        'is_main': image_meta.get('is_preview', False)
                    })
                    os.remove(local_image_path)
                    logger.info(f"User {user_id}: Deleted local image file {local_image_path}")
                except Exception as e:
                    logger.error(f"User {user_id}: Error uploading image {image_meta['file_path']}: {e}")

            # Check if the local images directory is empty, and if so, delete it
        if not os.listdir(local_images_directory):
            os.rmdir(local_images_directory)
            logger.info(f"User {user_id}: Removed empty folder: {local_images_directory}")

        if not image_urls:
            logger.error(f"User {user_id}: No images available for uploading")
            return JsonResponse({'error': 'No images available'}, status=400)

        coordinates = selected_building.get('coordinates')
        if not coordinates or len(coordinates) != 2:
            logger.error(f"User {user_id}: Invalid or missing coordinates in selected_building data.")
            return JsonResponse({'error': 'Invalid or missing coordinates'}, status=400)

        building = Building()
        building.name = selected_building.get('alternative_name', '')
        building.address = building_address
        building.construction_year = selected_building.get('constructionYear')
        building.type_of_use = selected_building.get('typeOfUse')
        building.tags = selected_building.get('tags', [])
        building.description = selected_building.get('description', '')
        building.timeline = selected_building.get('timeline', [])
        building.location = {"type": "Point", "coordinates": coordinates}
        building.image_urls = image_urls

        building.save()
        logger.info(f"User {user_id}: Building saved successfully with ID: {building.public_id}")

        # Clear session data related to the building
        for key in ['selected_building', 'images_metadata']:
            if key in request.session:
                del request.session[key]
        request.session.modified = True

        return JsonResponse({'status': 'success', 'building_id': str(building.public_id)})

    except Exception as e:
        logger.error(f"User {user_id}: Error occurred in publish_building method: {e}", exc_info=True)
        return JsonResponse({'error': 'Error processing building publication'}, status=500)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_building(request):
    user_id = request.user.id
    logger.info(f"User {user_id} initiated building update.")

    try:
        data = request.data
        building_id = data.get('_id')
        if not building_id:
            logger.error(f"User {user_id} did not provide a building ID.")
            return JsonResponse({'status': 'error', 'message': 'Building ID not provided'}, status=400)

        building = Building.objects.get(_id=BsonObjectId(building_id))
        logger.debug(f"User {user_id} updating existing building: {building_id}")

        # Process and update building fields
        if 'address' in data:
            building.address = data.get('address')
        if 'location' in data:
            building.location = json.loads(data.get('location'))
        if 'name' in data:
            building.name = data.get('name', '')
        if 'construction_year' in data:
            building.construction_year = int(data.get('construction_year'))
        if 'type_of_use' in data:
            building.type_of_use = data.get('type_of_use')
        if 'description' in data:
            building.description = data.get('description')
        if 'tags' in data:
            building.tags = json.loads(data.get('tags'))
        if 'active' in data:
            building.active = data.get('active', True)

        # Process timeline data
        if 'timeline' in data:
            timeline_data = json.loads(data.get('timeline'))
            building.timeline = timeline_data

        # TODO: Implement Logic for Images

        building.save()
        logger.info(f"User {user_id} successfully updated building: {building_id}")
        return JsonResponse({'status': 'success', 'message': 'Building updated successfully'})

    except Building.DoesNotExist:
        logger.error(f"User {user_id} tried to update a non-existing building: {building_id}")
        return JsonResponse({'status': 'error', 'message': 'Building not found'}, status=404)

    except Exception as e:
        logger.error(f"User {user_id} encountered an error in updating building: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@permission_classes([IsAuthenticated])
def set_buildings_active_status(request):
    user_id = request.user.id
    try:
        if request.method == 'POST':
            building_ids = request.POST.getlist('building_ids')
            active_status = request.POST.get('active_status') == 'true'
            Building.objects.filter(id__in=building_ids).update(active=active_status)
            logger.info(f"User {user_id} set active status to {active_status} for buildings {building_ids}")
            return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"User {user_id}: Error in set_buildings_active_status: {e}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@permission_classes([IsAuthenticated])
def delete_buildings(request):
    user_id = request.user.id
    try:
        if request.method == 'POST':
            building_ids = request.POST.getlist('building_ids')
            Building.objects.filter(id__in=building_ids).delete()
            logger.info(f"User {user_id} deleted buildings {building_ids}")
            return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"User {user_id}: Error in delete_buildings: {e}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

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



