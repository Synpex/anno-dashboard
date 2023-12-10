from django.urls import path
from .views import users_view, profile_view

urlpatterns = [
path('', users_view, name='users'),
path('profile', profile_view, name='profile'),
    ]