from django.urls import path
from .views.html_views import buildings_view, import_detail_view, import_images_view, import_timeline_view, import_position_view, import_review_view, import_audioguides_view, serve_temp_image

urlpatterns = [
path('temp/<str:image_path>', serve_temp_image, name='serve_temp_image'),
path('', buildings_view, name='buildings'),
path('import/detail', import_detail_view, name='import'),
path('import/images', import_images_view, name='import'),
path('import/timeline', import_timeline_view, name='import'),
path('import/position', import_position_view, name='import'),
path('import/review', import_review_view, name='import'),
path('import/audioguides', import_audioguides_view, name='import'),



]