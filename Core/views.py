# from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# This decorator ensures that only authenticated users can access the dashboard
@login_required
def dashboard_view(request):
    # You can add your logic here to pass context to your dashboard template
    context = {
        'section': 'dashboard',
        # Add more context variables here
    }
    return render(request, 'buildings.html', context)

@login_required

def login_view(request):
    context = {'section': 'login'}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return redirect('dashboard')  # Replace 'dashboard' with the name of your dashboard URL
        else:
            # Return an 'invalid login' error message.
            messages.error(request, 'Invalid username or password.')

    return render(request, 'registration/login.html', context)


