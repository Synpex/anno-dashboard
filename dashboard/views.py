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