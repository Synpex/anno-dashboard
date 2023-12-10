from django.shortcuts import render

# Create your views here.
def statistics_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'statistics',
        # Add more context variables here
    }
    return render(request, 'statistics.html', context)