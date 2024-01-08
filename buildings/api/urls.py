# your_app/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import BuildingViewSet, AudioguideViewSet
from buildings.views.api_views import BuildingByYearList, SortedBuildingsView, BuildingSearchView, api_proxy_view, \
update_building_details, update_search_params, upload_temp_images

router = DefaultRouter()
router.register(r'buildings', BuildingViewSet, basename='buildings')
router.register(r'audioguides', AudioguideViewSet, basename='audioguides')  # Register the audioguides route


urlpatterns = [
    path('buildings/session/images', upload_temp_images, name='updateSessionImages'),
    path('buildings/session/search', update_search_params, name='updateSessionSearch'),
    path('buildings/session/details', update_building_details, name='updateSessionDetails'),
    path('buildings/search/', BuildingSearchView.as_view(), name='building-search'),
    path('buildings/slim/', SortedBuildingsView.as_view(), name='building-sorted'),
    path('', include(router.urls)),
    path('buildings/year/<int:year>/', BuildingByYearList.as_view(), name='building-by-year'),
    path('buildings/proxy/bag', api_proxy_view, name='api_proxy')
]
