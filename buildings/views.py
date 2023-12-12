from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.

# This decorator ensures that only authenticated users can access the dashboard
@login_required
def buildings_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'buildings',
        # Add more context variables here
    }
    return render(request, 'buildings.html', context)
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
    context = {
        'section': 'import',
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