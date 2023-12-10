from django.urls import path
from .views import dashboard_view, login_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('login', login_view, name='login')
]