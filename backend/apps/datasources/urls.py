"""
URL configuration for datasources application.
"""

from django.urls import path
from . import views

app_name = 'datasources'

urlpatterns = [
    # Sync endpoints (Admin only)
    path('sync/leagues/', views.sync_leagues, name='sync-leagues'),
    path('sync/teams/', views.sync_teams, name='sync-teams'),
    path('sync/matches/', views.sync_matches, name='sync-matches'),
    path('sync/full/', views.sync_full, name='sync-full'),
    
    # Status endpoint
    path('sync/status/', views.sync_status, name='sync-status'),
]
