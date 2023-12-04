# your_app/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import BuildingViewSet

router = DefaultRouter()
router.register(r'buildings', BuildingViewSet, basename='building')

urlpatterns = [
    path('', include(router.urls)),
]
