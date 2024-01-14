# from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from prometheus_client import generate_latest
from django.http import HttpResponse

# This decorator ensures that only authenticated users can access the dashboard
@login_required
def dashboard_view(request):
    # Redirect to the /buildings URL
    return redirect('/buildings')

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


def metrics(request):
    return HttpResponse(generate_latest(), content_type='text/plain')
