from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from users.models.profile_model import UserProfile


@login_required

def users_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'users',
        # Add more context variables here
    }
    return render(request, 'users.html', context)

@login_required

def profile_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'profile.html', {'user_profile': user_profile})
