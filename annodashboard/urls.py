"""
URL configuration for annodashboard project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# project/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Anno Amsterdam CoreAPI",
      default_version='v1',
      description="The internal API for the Anno Amsterdam project's CMS",
      terms_of_service="https://anno.amsterdam/terms/",
      contact=openapi.Contact(email="preis@computer.org"),
      license=openapi.License(name="MIT"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),

)

urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),
    path('admin/', admin.site.urls),
    #path('api/core/', include('Core.api.urls')),
    path('api/building/', include('buildings.api.urls')),
    #path('api/users/', include('users.api.urls')),
    # path('api/statistic/', include('statistic.api.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', include('Core.urls')),
    path("accounts/", include("django.contrib.auth.urls")),
    path('buildings/', include('buildings.urls')),
    path('users/', include('users.urls')),
    path('statistics/', include('stats.urls')),

]
