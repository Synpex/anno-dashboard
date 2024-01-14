from django.urls import path
from .views import dashboard_view, login_view, metrics

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('metrics/', metrics, name='metrics')
]