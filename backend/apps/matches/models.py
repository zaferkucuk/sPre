"""
Match models for the sPre application.

This module defines models for sports matches, teams, leagues, and predictions.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Sport(models.Model):
    """
    Sport type model.
    
    Represents different sports (Football, Basketball, Tennis, etc.)
    
    Attributes:
        name (CharField): Sport name
        slug (SlugField): URL-friendly sport identifier
        description (TextField): Sport description
        is_active (BooleanField): Whether sport is active
    """
    
    name = models.CharField(
        _('name'),
        max_length=100,
        unique=True,
        help_text=_('Sport name (e.g., Football, Basketball)')
    )
    
    slug = models.SlugField(
        _('slug'),
        max_length=100,
        unique=True,
        help_text=_('URL-friendly identifier')
    )
    
    description = models.TextField(
        _('description'),
        blank=True,
        null=True,
        help_text=_('Sport description')
    )
    
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_('Whether this sport is active')
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('sport')
        verbose_name_plural = _('sports')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class League(models.Model):
    """
    League/Competition model.
    
    Represents sports leagues or competitions.
    
    Attributes:
        sport (ForeignKey): Related sport
        name (CharField): League name
        country (CharField): League country
        season (CharField): Current season
        logo (URLField): League logo URL
    """
    
    sport = models.ForeignKey(
        Sport,
        on_delete=models.CASCADE,
        related_name='leagues',
        verbose_name=_('sport')
    )
    
    external_id = models.CharField(
        _('external ID'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('ID from external data source')
    )
    
    name = models.CharField(
        _('name'),
        max_length=200,
        help_text=_('League name')
    )
    
    country = models.CharField(
        _('country'),
        max_length=100,
        help_text=_('Country or region')
    )
    
    season = models.CharField(
        _('season'),
        max_length=20,
        help_text=_('Season (e.g., 2024-2025)')
    )
    
    logo = models.URLField(
        _('logo URL'),
        blank=True,
        null=True,
        help_text=_('League logo URL')
    )
    
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_('Whether this league is active')
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('league')
        verbose_name_plural = _('leagues')
        ordering = ['country', 'name']
        unique_together = [['sport', 'external_id']]
        indexes = [
            models.Index(fields=['sport', 'country']),
            models.Index(fields=['external_id']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.country})"


class Team(models.Model):
    """
    Team model.
    
    Represents sports teams.
    
    Attributes:
        sport (ForeignKey): Related sport
        name (CharField): Team name
        country (CharField): Team country
        logo (URLField): Team logo URL
        founded (IntegerField): Year founded
    """
    
    sport = models.ForeignKey(
        Sport,
        on_delete=models.CASCADE,
        related_name='teams',
        verbose_name=_('sport')
    )
    
    external_id = models.CharField(
        _('external ID'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('ID from external data source')
    )
    
    name = models.CharField(
        _('name'),
        max_length=200,
        help_text=_('Team name')
    )
    
    code = models.CharField(
        _('code'),
        max_length=10,
        blank=True,
        null=True,
        help_text=_('Team code (e.g., MUN, BAR)')
    )
    
    country = models.CharField(
        _('country'),
        max_length=100,
        help_text=_('Team country')
    )
    
    logo = models.URLField(
        _('logo URL'),
        blank=True,
        null=True,
        help_text=_('Team logo URL')
    )
    
    founded = models.IntegerField(
        _('founded year'),
        blank=True,
        null=True,
        help_text=_('Year the team was founded')
    )
    
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_('Whether this team is active')
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('team')
        verbose_name_plural = _('teams')
        ordering = ['name']
        unique_together = [['sport', 'external_id']]
        indexes = [
            models.Index(fields=['sport', 'country']),
            models.Index(fields=['external_id']),
        ]
    
    def __str__(self):
        return self.name


class Match(models.Model):
    """
    Match model.
    
    Represents a sports match between two teams.
    
    Attributes:
        league (ForeignKey): Related league
        home_team (ForeignKey): Home team
        away_team (ForeignKey): Away team
        match_date (DateTimeField): Match date and time
        status (CharField): Match status
        home_score (IntegerField): Home team score
        away_score (IntegerField): Away team score
    """
    
    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', _('Scheduled')
        LIVE = 'LIVE', _('Live')
        FINISHED = 'FINISHED', _('Finished')
        POSTPONED = 'POSTPONED', _('Postponed')
        CANCELLED = 'CANCELLED', _('Cancelled')
    
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name='matches',
        verbose_name=_('league')
    )
    
    external_id = models.CharField(
        _('external ID'),
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        help_text=_('ID from external data source')
    )
    
    home_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='home_matches',
        verbose_name=_('home team')
    )
    
    away_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='away_matches',
        verbose_name=_('away team')
    )
    
    match_date = models.DateTimeField(
        _('match date'),
        help_text=_('Date and time of the match')
    )
    
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
        help_text=_('Match status')
    )
    
    home_score = models.IntegerField(
        _('home score'),
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text=_('Home team score')
    )
    
    away_score = models.IntegerField(
        _('away score'),
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text=_('Away team score')
    )
    
    venue = models.CharField(
        _('venue'),
        max_length=200,
        blank=True,
        null=True,
        help_text=_('Match venue/stadium')
    )
    
    referee = models.CharField(
        _('referee'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Match referee')
    )
    
    statistics = models.JSONField(
        _('statistics'),
        default=dict,
        blank=True,
        help_text=_('Match statistics (shots, possession, etc.)')
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('match')
        verbose_name_plural = _('matches')
        ordering = ['-match_date']
        indexes = [
            models.Index(fields=['league', 'match_date']),
            models.Index(fields=['status', 'match_date']),
            models.Index(fields=['external_id']),
        ]
    
    def __str__(self):
        return f"{self.home_team} vs {self.away_team} ({self.match_date.date()})"
    
    @property
    def is_finished(self):
        """Check if match is finished."""
        return self.status == self.Status.FINISHED
    
    @property
    def is_live(self):
        """Check if match is live."""
        return self.status == self.Status.LIVE


class Prediction(models.Model):
    """
    Prediction model.
    
    Stores predictions for matches.
    
    Attributes:
        match (ForeignKey): Related match
        user (ForeignKey): User who made prediction (optional for ML predictions)
        prediction_type (CharField): Type of prediction
        predicted_home_score (IntegerField): Predicted home score
        predicted_away_score (IntegerField): Predicted away score
        confidence (FloatField): Prediction confidence (0-100)
        is_correct (BooleanField): Whether prediction was correct
    """
    
    class PredictionType(models.TextChoices):
        USER = 'USER', _('User Prediction')
        ML_MODEL = 'ML_MODEL', _('ML Model Prediction')
        STATISTICAL = 'STATISTICAL', _('Statistical Analysis')
    
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='predictions',
        verbose_name=_('match')
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='predictions',
        verbose_name=_('user'),
        blank=True,
        null=True,
        help_text=_('User who made the prediction (null for ML predictions)')
    )
    
    prediction_type = models.CharField(
        _('prediction type'),
        max_length=20,
        choices=PredictionType.choices,
        default=PredictionType.USER,
        help_text=_('Type of prediction')
    )
    
    predicted_home_score = models.IntegerField(
        _('predicted home score'),
        validators=[MinValueValidator(0)],
        help_text=_('Predicted score for home team')
    )
    
    predicted_away_score = models.IntegerField(
        _('predicted away score'),
        validators=[MinValueValidator(0)],
        help_text=_('Predicted score for away team')
    )
    
    confidence = models.FloatField(
        _('confidence'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Prediction confidence percentage (0-100)')
    )
    
    reasoning = models.TextField(
        _('reasoning'),
        blank=True,
        null=True,
        help_text=_('Reasoning behind the prediction')
    )
    
    is_correct = models.BooleanField(
        _('is correct'),
        blank=True,
        null=True,
        help_text=_('Whether prediction was correct (null if match not finished)')
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('prediction')
        verbose_name_plural = _('predictions')
        ordering = ['-created_at']
        unique_together = [['match', 'user', 'prediction_type']]
        indexes = [
            models.Index(fields=['match', 'user']),
            models.Index(fields=['prediction_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"Prediction for {self.match} ({self.prediction_type})"
    
    @property
    def predicted_winner(self):
        """Get predicted winner."""
        if self.predicted_home_score > self.predicted_away_score:
            return 'HOME'
        elif self.predicted_away_score > self.predicted_home_score:
            return 'AWAY'
        return 'DRAW'
