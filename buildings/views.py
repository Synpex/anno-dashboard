from django.shortcuts import render

# Create your views here.
def buildings_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'buildings',
        # Add more context variables here
    }
    return render(request, 'buildings.html', context)

def import_detail_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'import',
        # Add more context variables here
    }
    return render(request, 'import_detail.html', context)

def import_images_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'import',
        # Add more context variables here
    }
    return render(request, 'import_images.html', context)


def import_timeline_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'import',
        # Add more context variables here
    }
    return render(request, 'import_timeline.html', context)

def import_position_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'import',
        # Add more context variables here
    }
    return render(request, 'import_position.html', context)

def import_review_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'import',
        # Add more context variables here
    }
    return render(request, 'import_review.html', context)