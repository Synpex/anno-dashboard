import json
import os
import uuid

from django.core.files.storage import FileSystemStorage
from django.core.serializers.json import DjangoJSONEncoder
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.serializers import serialize
from djongo.models import ObjectIdField
from bson import ObjectId as BsonObjectId

from buildings.building_form import BuildingForm
from buildings.models.building_model import Building


# This decorator ensures that only authenticated users can access the dashboard
@login_required
def buildings_view(request):

    # Fetch all buildings
    buildings = Building.objects.all()
    # Count buildings
    buildings_count = buildings.count()
    # Count buildings without images
    buildings_without_images_count = Building.objects.filter(image_urls=None).count()
    # Count buildings without a timeline
    buildings_with_incomplete_timeline_count = Building.objects.exclude(timeline__isnull=False).count()
    # Serialize Buildings QuerySet into JSON
    buildings_json = serialize('json', buildings)  # use json.dumps instead!!!

    mapbox_access_token = settings.MAPBOX_ACCESS_TOKEN
    context = {
        'section': 'buildings',
        'mapbox_access_token': mapbox_access_token,
        'buildings': buildings,
        'buildings_count': buildings_count,
        'buildings_with_incomplete_timeline_count': buildings_with_incomplete_timeline_count,
        'buildings_without_images_count': buildings_without_images_count,
        'buildings_json' : buildings_json,
    }
    return render(request, 'buildings.html', context)

@login_required
def edit_building_view(request, building_public_id):
    # Prepare your context data
    queryset = Building.objects.all()
    selected_building = queryset.get(_id=BsonObjectId(building_public_id))
    form = BuildingForm()

    if request.method == 'POST':
        form = BuildingForm(request.POST, instance=selected_building)

        if form.is_valid():
            return HttpResponse('ok')

    context = {
                  'section': 'buildings',
                  'selected_building': selected_building,
                  'form': form,
    }
    return render(request, 'edit_building.html', context)


@login_required
def import_view(request):
    # You can add your logic here to pass context to your dashboard template
    mapbox_access_token = settings.MAPBOX_ACCESS_TOKEN
    context = {
        'section': 'import',
        'mapbox_access_token': mapbox_access_token,
    }
    return render(request, 'import.html', context)


@login_required
def import_detail_view(request):
    selected_building = None
    building_detail = None

    # If selected_building is stored in the session, retrieve it
    if 'selected_building' in request.session:
        selected_building = request.session['selected_building']

    # Retrieve the building from the session
    if 'building_detail' in request.session:
        building_detail = request.session['building_detail']

    # Prepare your context data
    context = {
        'section': 'import',
        'selected_building': selected_building,
        'building_detail': building_detail,
        # Add more context variables here as needed
    }

    return render(request, 'import_detail.html', context)


@login_required
def import_images_view(request):
    if request.method == 'POST':
        # Process the uploaded images
        images = request.FILES.getlist('images')
        sources = request.POST.getlist('source')  # List of sources for each image
        years = request.POST.getlist('year')  # List of years for each image
        preview_ids = request.POST.getlist('preview_id')  # IDs of the preview images

        # Initialize the session variables if they don't exist
        if 'images_metadata' not in request.session:
            request.session['images_metadata'] = []

        fs = FileSystemStorage(location=settings.TEMP_IMAGE_STORAGE)  # Use a temporary storage location

        for index, image in enumerate(images):
            # Generate a new filename to avoid conflicts
            temp_filename = str(uuid.uuid4()) + os.path.splitext(image.name)[1]
            filename = fs.save(temp_filename, image)  # Save the file to temporary storage

            # Append metadata for each image
            request.session['images_metadata'].append({
                'file_path': fs.url(filename),
                'source': sources[index] if index < len(sources) else '',
                'year': years[index] if index < len(years) else '',
                'is_preview': str(index) in preview_ids,
            })

        # Save the session (required if using a file-based session backend)
        request.session.modified = True

        # Redirect to the next step or back to the form for additional uploads
        return redirect('next_view_name')  # Replace with the name of your next view or URL

    # Existing context for rendering the form
    context = {
        'section': 'import',
        'images_metadata_json': json.dumps([], cls=DjangoJSONEncoder),
    }

    # Only update images_metadata_json in the context if it's present in the session
    if 'images_metadata' in request.session:
        context['images_metadata_json'] = json.dumps(request.session['images_metadata'], cls=DjangoJSONEncoder)

    # In your Django view
    print(context['images_metadata_json'])  # Check the console where your server is running to see the output

    return render(request, 'import_images.html', context)

@login_required
def import_timeline_view(request):
    # Retrieve timeline data from the session
    timeline_data = request.session.get('timeline', [])

    # Pass the timeline data to the context after converting it to JSON
    context = {
        'section': 'import',
        'timeline_data_json': json.dumps(timeline_data)  # Convert to JSON for use in JavaScript
    }
    return render(request, 'import_timeline.html', context)

def import_audioguides_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'import',
        # Add more context variables here
    }
    return render(request, 'import_audioguides.html', context)

@login_required

def import_position_view(request):
    # Retrieve session data
    search_params = request.session.get('search_params')
    selected_building = request.session.get('selected_building')

    print(search_params)
    print(selected_building)

    # You can add your logic here to pass context to your dashboard template
    mapbox_access_token = settings.MAPBOX_ACCESS_TOKEN
    api_base_url = settings.BAG_API_BASE_URL
    context = {
        'section': 'import',
        'mapbox_access_token': mapbox_access_token,
        'api_base_url': api_base_url,
        'search_params': search_params if search_params is not None else {},
        'selected_building': selected_building if selected_building is not None else {},
    }
    return render(request, 'import_position.html', context)

@login_required
def import_review_view(request):
    # Extract specific fields from the session data
    search_params = request.session.get('search_params', {})
    selected_building = request.session.get('selected_building', {})
    uploaded_images = request.session.get('uploaded_images', [])
    images_metadata = request.session.get('images_metadata', [])
    timeline = request.session.get('timeline', [])

    # You can add your logic here to pass context to your dashboard template
    context = {
        'MEDIA_URL': settings.MEDIA_URL,
        'section': 'import',
        'search_params': search_params,
        'selected_building': selected_building,
        'selected_building_json': json.dumps(selected_building),
        'uploaded_images_json': json.dumps(uploaded_images),
        'timeline_json': json.dumps(timeline),
        'timeline': timeline,
        'images_metadata': images_metadata,
        # Add more context variables here
    }

    return render(request, 'import_review.html', context)


@login_required
def serve_temp_image(request, image_path):
    user_id = request.user.id
    file_path = os.path.join(settings.MEDIA_ROOT, f'temp/user_{user_id}_{request.session.session_key}', image_path)

    # Check if the file belongs to the user
    if not os.path.isfile(file_path) or str(user_id) not in image_path:
        raise Http404("Image does not exist or you do not have permission to view it.")

    with open(file_path, "rb") as f:
        return HttpResponse(f.read(), content_type="image/jpeg")  # or the appropriate image mime type



