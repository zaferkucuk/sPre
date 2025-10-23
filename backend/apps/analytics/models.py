"""
Analytics models for the sPre application.

This module defines models for team statistics, match analytics, and ML models.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.matches.models import Team, Match


class TeamStatistics(models.Model):
    """
    Team statistics model for analytics.
    
    Stores aggregated statistics for teams focused on analytics and predictions.
    Note: This is separate from matches.TeamStatistics which stores seasonal data.
    
    Attributes:
        team (ForeignKey): Related team
        season (CharField): Season identifier
        matches_played (IntegerField): Total matches played
        wins (IntegerField): Number of wins
        draws (IntegerField): Number of draws
        losses (IntegerField): Number of losses
        goals_scored (IntegerField): Total goals scored
        goals_conceded (IntegerField): Total goals conceded
        clean_sheets (IntegerField): Number of clean sheets
    """
    
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='analytics_statistics',  # Changed from 'statistics' to avoid clash
        verbose_name=_('team'),
        help_text=_('Reference to the team')
    )
    
    season = models.CharField(
        _('season'),
        max_length=20,
        help_text=_('Season identifier (e.g., 2024-2025)')
    )
    
    matches_played = models.IntegerField(
        _('matches played'),
        default=0,
        help_text=_('Total matches played')
    )
    
    wins = models.IntegerField(
        _('wins'),
        default=0,
        help_text=_('Number of wins')
    )
    
    draws = models.IntegerField(
        _('draws'),
        default=0,
        help_text=_('Number of draws')
    )
    
    losses = models.IntegerField(
        _('losses'),
        default=0,
        help_text=_('Number of losses')
    )
    
    goals_scored = models.IntegerField(
        _('goals scored'),
        default=0,
        help_text=_('Total goals scored')
    )
    
    goals_conceded = models.IntegerField(
        _('goals conceded'),
        default=0,
        help_text=_('Total goals conceded')
    )
    
    clean_sheets = models.IntegerField(
        _('clean sheets'),
        default=0,
        help_text=_('Number of clean sheets (matches without conceding)')
    )
    
    form = models.JSONField(
        _('recent form'),
        default=list,
        blank=True,
        help_text=_('Recent match results (W/D/L)')
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'analytics_team_statistics'  # Distinct table name
        verbose_name = _('team analytics statistics')
        verbose_name_plural = _('team analytics statistics')
        unique_together = [['team', 'season']]
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['team', 'season']),
            models.Index(fields=['season']),
        ]
    
    def __str__(self):
        return f"{self.team.name} - {self.season} (Analytics)"
    
    @property
    def points(self):
        """Calculate total points (3 for win, 1 for draw)."""
        return (self.wins * 3) + self.draws
    
    @property
    def goal_difference(self):
        """Calculate goal difference."""
        return self.goals_scored - self.goals_conceded
    
    @property
    def win_rate(self):
        """Calculate win rate percentage."""
        if self.matches_played == 0:
            return 0
        return (self.wins / self.matches_played) * 100


class MatchAnalytics(models.Model):
    """
    Match analytics model.
    
    Stores detailed analytics and predictions for matches.
    
    Attributes:
        match (OneToOneField): Related match
        home_win_probability (FloatField): Probability of home win
        draw_probability (FloatField): Probability of draw
        away_win_probability (FloatField): Probability of away win
        expected_goals_home (FloatField): Expected goals for home team
        expected_goals_away (FloatField): Expected goals for away team
        confidence_score (FloatField): Overall confidence in prediction
    """
    
    match = models.OneToOneField(
        Match,
        on_delete=models.CASCADE,
        related_name='analytics',
        verbose_name=_('match')
    )
    
    home_win_probability = models.FloatField(
        _('home win probability'),
        default=0.0,
        help_text=_('Probability of home team winning (0-100)')
    )
    
    draw_probability = models.FloatField(
        _('draw probability'),
        default=0.0,
        help_text=_('Probability of draw (0-100)')
    )
    
    away_win_probability = models.FloatField(
        _('away win probability'),
        default=0.0,
        help_text=_('Probability of away team winning (0-100)')
    )
    
    expected_goals_home = models.FloatField(
        _('expected goals home'),
        default=0.0,
        help_text=_('Expected goals for home team')
    )
    
    expected_goals_away = models.FloatField(
        _('expected goals away'),
        default=0.0,
        help_text=_('Expected goals for away team')
    )
    
    confidence_score = models.FloatField(
        _('confidence score'),
        default=0.0,
        help_text=_('Overall confidence in prediction (0-100)')
    )
    
    factors = models.JSONField(
        _('analysis factors'),
        default=dict,
        blank=True,
        help_text=_('Factors considered in analysis')
    )
    
    model_version = models.CharField(
        _('model version'),
        max_length=50,
        blank=True,
        null=True,
        help_text=_('Version of ML model used')
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'match_analytics'
        verbose_name = _('match analytics')
        verbose_name_plural = _('match analytics')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['match']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Analytics for {self.match}"
    
    @property
    def most_likely_outcome(self):
        """Get most likely match outcome."""
        probs = {
            'HOME_WIN': self.home_win_probability,
            'DRAW': self.draw_probability,
            'AWAY_WIN': self.away_win_probability,
        }
        return max(probs, key=probs.get)
