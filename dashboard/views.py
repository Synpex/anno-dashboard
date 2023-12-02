# from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# This decorator ensures that only authenticated users can access the dashboard
# @login_required
def dashboard_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'dashboard',
        # Add more context variables here
    }
    return render(request, 'base.html', context)

def buildings_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'buildings',
        # Add more context variables here
    }
    return render(request, 'buildings.html', context)

def import_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'import',
        # Add more context variables here
    }
    return render(request, 'import_detail.html', context)


def users_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'users',
        # Add more context variables here
    }
    return render(request, 'users.html', context)

def statistics_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'statistics',
        # Add more context variables here
    }
    return render(request, 'statistics.html', context)

def profile_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        # TODO: Implement dynamic retrieval of userID
        # 'section': f'{user}',
        'section': 'user123',
        # Add more context variables here
    }
    return render(request, 'profile.html', context)