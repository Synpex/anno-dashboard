# your_app/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import BuildingViewSet, AudioguideViewSet
from ..views import BuildingByYearList

router = DefaultRouter()
router.register(r'buildings', BuildingViewSet, basename='building')
router.register(r'audioguides', AudioguideViewSet, basename='audioguide')  # Register the audioguides route


urlpatterns = [
    path('', include(router.urls)),
    path('buildings/year/<int:year>/', BuildingByYearList.as_view(), name='building-by-year'),
    path('buildings/<str:id>/', BuildingViewSet.as_view({'get': 'retrieve'}), name='building-detail'),
]
