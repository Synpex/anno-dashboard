# your_app/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import BuildingViewSet, AudioguideViewSet
from buildings.views.api_views import BuildingByYearList, SortedBuildingsView

router = DefaultRouter()
router.register(r'buildings', BuildingViewSet, basename='building')
router.register(r'audioguides', AudioguideViewSet, basename='audioguide')  # Register the audioguides route


urlpatterns = [
    path('buildings/sorted/', SortedBuildingsView.as_view(), name='building-sorted'),
    path('', include(router.urls)),
    path('buildings/year/<int:year>/', BuildingByYearList.as_view(), name='building-by-year'),
]
