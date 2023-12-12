from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
@login_required

def statistics_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'statistics',
        # Add more context variables here
    }
    return render(request, 'statistics.html', context)