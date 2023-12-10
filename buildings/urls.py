from django.urls import path
from .views import buildings_view, import_detail_view, import_images_view, import_timeline_view, import_position_view, import_review_view

urlpatterns = [
path('', buildings_view, name='buildings'),
path('import/detail', import_detail_view, name='import'),
path('import/images', import_images_view, name='import'),
path('import/timeline', import_timeline_view, name='import'),
path('import/position', import_position_view, name='import'),
path('import/review', import_review_view, name='import'),]