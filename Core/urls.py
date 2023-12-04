from django.urls import path
from .views import dashboard_view,buildings_view, users_view, import_view, statistics_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('buildings', buildings_view, name='buildings'),
    path('users', users_view, name='users'),
    path('import', import_view, name='import'),
    path('statistics', statistics_view, name='statistics'),
    # TODO: Implement dynamic retrieval of userID
    path('user123', users_view, name='user123'),

]