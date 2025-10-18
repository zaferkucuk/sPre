"""
URL configuration for datasources application.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DataSourceViewSet, SyncLogViewSet

app_name = 'datasources'

router = DefaultRouter()
router.register(r'sources', DataSourceViewSet, basename='source')
router.register(r'sync-logs', SyncLogViewSet, basename='sync-log')

urlpatterns = [
    path('', include(router.urls)),
]
