from django.urls import path
from .views import users_list_view, profile_view, update_user_permissions

urlpatterns = [
path('', users_list_view, name='users'),
path('profile', profile_view, name='profile'),
path('update-permissions', update_user_permissions, name='update_user_permissions'),
    ]