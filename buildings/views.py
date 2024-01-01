from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
# Create your views here.

from rest_framework import generics
from buildings.models.building_model import Building
from buildings.api.api import BuildingSerializer

class BuildingByYearList(generics.ListAPIView):
    serializer_class = BuildingSerializer

    def get_queryset(self):
        """
        This view should return a list of all buildings for
        the construction year as determined by the year portion of the URL.
        """
        year = self.kwargs['year']
        return Building.objects.filter(construction_year=year)


# This decorator ensures that only authenticated users can access the dashboard
@login_required
def buildings_view(request):
    # You can add your logic here to pass context to your dashboard template
    mapbox_access_token = settings.MAPBOX_ACCESS_TOKEN
    context = {
        'section': 'buildings',
        'mapbox_access_token': mapbox_access_token,
        # Add more context variables here
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

def import_audioguides_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'import',
        # Add more context variables here
    }
    return render(request, 'import_audioguides.html', context)

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

