from django.shortcuts import render

def users_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'users',
        # Add more context variables here
    }
    return render(request, 'users.html', context)


def profile_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        # TODO: Implement dynamic retrieval of userID
        # 'section': f'{user}',
        'section': 'user',
        # Add more context variables here
    }
    return render(request, 'profile.html', context)
