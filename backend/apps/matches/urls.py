"""
URL configuration for matches application.
"""

from django.urls import path
from . import views

app_name = 'matches'

urlpatterns = [
    # Sports endpoints
    path('sports/', views.sports_list, name='sports-list'),
    path('sports/<int:sport_id>/', views.sport_detail, name='sport-detail'),
    
    # Leagues endpoints
    path('leagues/', views.leagues_list, name='leagues-list'),
    path('leagues/<int:league_id>/', views.league_detail, name='league-detail'),
    
    # Teams endpoints
    path('teams/', views.teams_list, name='teams-list'),
    path('teams/<int:team_id>/', views.team_detail, name='team-detail'),
    path('teams/<int:team_id>/matches/', views.team_matches, name='team-matches'),
    
    # Matches endpoints
    path('matches/', views.matches_list, name='matches-list'),
    path('matches/<int:match_id>/', views.match_detail, name='match-detail'),
    
    # Predictions endpoints
    path('predictions/', views.predictions_list, name='predictions-list'),
    path('predictions/create/', views.prediction_create, name='prediction-create'),
    
    # Health check
    path('health/', views.health_check, name='health-check'),
]
