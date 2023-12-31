from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings

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

    mapbox_access_token = settings.MAPBOX_ACCESS_TOKEN
    context = {
        'section': 'buildings',
        'mapbox_access_token': mapbox_access_token,
        'buildings': buildings,
        'buildings_count': buildings_count,
        'buildings_with_incomplete_timeline_count': buildings_with_incomplete_timeline_count,
        'buildings_without_images_count': buildings_without_images_count
    }
    return render(request, 'buildings.html', context)

@login_required
def import_view(request):
    # You can add your logic here to pass context to your dashboard template
    mapbox_access_token = settings.MAPBOX_ACCESS_TOKEN
    context = {
        'section': 'import',
        'mapbox_access_token': mapbox_access_token,
        # Add more context variables here
    }
    return render(request, 'import.html', context)


@login_required
def import_detail_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'import',
        # Add more context variables here
    }
    return render(request, 'import_detail.html', context)

@login_required
def import_images_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'import',
        # Add more context variables here
    }
    return render(request, 'import_images.html', context)

@login_required

def import_timeline_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'import',
        # Add more context variables here
    }
    return render(request, 'import_timeline.html', context)
@login_required

def import_position_view(request):
    # You can add your logic here to pass context to your dashboard template
    mapbox_access_token = settings.MAPBOX_ACCESS_TOKEN
    context = {
        'section': 'import',
        'mapbox_access_token': mapbox_access_token,
        # Add more context variables here
    }
    return render(request, 'import_position.html', context)
@login_required

def import_review_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'import',
        # Add more context variables here
    }
    return render(request, 'import_review.html', context)

