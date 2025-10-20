"""
Match models for the sPre application.

This module defines models for sports matches, teams, leagues, seasons, statistics, and predictions.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Sport(models.Model):
    """Sport type model."""
    
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
        db_table = 'sports'
        verbose_name = _('sport')
        verbose_name_plural = _('sports')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Season(models.Model):
    """
    Season model for tracking sports seasons.
    """
    
    name = models.CharField(
        _('name'),
        max_length=50,
        unique=True,
        help_text=_('Season name (e.g., 2025-2026)')
    )
    
    year = models.IntegerField(
        _('year'),
        help_text=_('Starting year of the season')
    )
    
    start_date = models.DateField(
        _('start date'),
        help_text=_('Season start date')
    )
    
    end_date = models.DateField(
        _('end date'),
        help_text=_('Season end date')
    )
    
    is_current = models.BooleanField(
        _('is current'),
        default=False,
        help_text=_('Whether this is the current season')
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'seasons'
        verbose_name = _('season')
        verbose_name_plural = _('seasons')
        ordering = ['-year']
        indexes = [
            models.Index(fields=['year']),
            models.Index(fields=['is_current']),
        ]
    
    def __str__(self):
        return self.name


class League(models.Model):
    """League/Competition model."""
    
    sport = models.ForeignKey(
        Sport,
        on_delete=models.CASCADE,
        related_name='leagues',
        verbose_name=_('sport'),
        db_column='sport_id'
    )
    
    external_id = models.CharField(
        _('external ID'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('ID from external data source (API-Football)')
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
        db_table = 'leagues'
        verbose_name = _('league')
        verbose_name_plural = _('leagues')
        ordering = ['country', 'name']
        indexes = [
            models.Index(fields=['sport', 'country']),
            models.Index(fields=['external_id']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.country})"
    
    @property
    def api_id(self):
        """Convenience property for API ID."""
        return int(self.external_id) if self.external_id else None


class Team(models.Model):
    """Team model."""
    
    sport = models.ForeignKey(
        Sport,
        on_delete=models.CASCADE,
        related_name='teams',
        verbose_name=_('sport'),
        db_column='sport_id'
    )
    
    league = models.ForeignKey(
        League,
        on_delete=models.SET_NULL,
        related_name='teams',
        verbose_name=_('league'),
        null=True,
        blank=True,
        db_column='league_id'
    )
    
    external_id = models.CharField(
        _('external ID'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('ID from external data source (API-Football)')
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
        db_table = 'teams'
        verbose_name = _('team')
        verbose_name_plural = _('teams')
        ordering = ['name']
        indexes = [
            models.Index(fields=['sport', 'country']),
            models.Index(fields=['external_id']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def api_id(self):
        """Convenience property for API ID."""
        return int(self.external_id) if self.external_id else None


class TeamStatistics(models.Model):
    """
    Stores comprehensive seasonal statistics for teams.
    
    Updated daily for basic stats (goals, wins, etc.).
    Updated weekly for xG data (only Tier 1 leagues).
    """
    
    # Relationships
    team = models.ForeignKey(
        Team, 
        on_delete=models.CASCADE,
        related_name='statistics',
        db_column='team_id'
    )
    season = models.ForeignKey(
        Season, 
        on_delete=models.CASCADE,
        related_name='team_statistics',
        db_column='season_id'
    )
    
    # Basic Statistics (Updated Daily)
    matches_played = models.IntegerField(
        default=0,
        help_text="Total matches played in the season"
    )
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    goals_diff = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    
    # Home/Away Statistics
    home_matches = models.IntegerField(default=0)
    home_wins = models.IntegerField(default=0)
    home_draws = models.IntegerField(default=0)
    home_losses = models.IntegerField(default=0)
    home_goals_for = models.IntegerField(default=0)
    home_goals_against = models.IntegerField(default=0)
    
    away_matches = models.IntegerField(default=0)
    away_wins = models.IntegerField(default=0)
    away_draws = models.IntegerField(default=0)
    away_losses = models.IntegerField(default=0)
    away_goals_for = models.IntegerField(default=0)
    away_goals_against = models.IntegerField(default=0)
    
    # Expected Goals (xG) - Only for Tier 1 Leagues
    xg_for = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Expected Goals For - Total xG generated by the team"
    )
    xg_against = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Expected Goals Against - Total xG allowed to opponents"
    )
    xg_diff = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="xG Difference (xG_for - xG_against)"
    )
    xg_performance = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Performance vs xG (goals_for - xG_for). Positive = overperforming"
    )
    
    # Calculated Metrics
    goals_per_match = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00
    )
    goals_conceded_per_match = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00
    )
    
    # Form (Last 5 matches)
    form = models.CharField(
        max_length=5,
        blank=True,
        help_text="Last 5 match results (W/D/L). Example: WWDLW"
    )
    
    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    xg_last_updated = models.DateTimeField(null=True, blank=True)
    data_source = models.CharField(max_length=50, default='api-football')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'team_statistics'
        unique_together = ['team', 'season']
        verbose_name = 'Team Statistics'
        verbose_name_plural = 'Team Statistics'
        ordering = ['-points', '-goals_diff']
        indexes = [
            models.Index(fields=['team', 'season']),
            models.Index(fields=['season', 'points']),
        ]
    
    def __str__(self):
        return f"{self.team.name} - {self.season.name}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate derived fields before saving."""
        # Calculate goal difference
        self.goals_diff = self.goals_for - self.goals_against
        
        # Calculate averages
        if self.matches_played > 0:
            self.goals_per_match = round(
                self.goals_for / self.matches_played, 
                2
            )
            self.goals_conceded_per_match = round(
                self.goals_against / self.matches_played, 
                2
            )
        
        # Calculate xG difference
        if self.xg_for is not None and self.xg_against is not None:
            self.xg_diff = round(float(self.xg_for) - float(self.xg_against), 2)
        
        # Calculate xG performance
        if self.xg_for is not None:
            self.xg_performance = round(
                float(self.goals_for) - float(self.xg_for), 
                2
            )
        
        super().save(*args, **kwargs)
    
    @property
    def has_xg_data(self):
        """Check if team has xG data available."""
        return self.xg_for is not None
    
    @property
    def win_percentage(self):
        """Calculate win percentage."""
        if self.matches_played == 0:
            return 0.0
        return round((self.wins / self.matches_played) * 100, 2)


class Fixture(models.Model):
    """
    Stores upcoming matches and results.
    
    Used for:
    - Match predictions (pre-match analysis)
    - Historical results tracking
    - xG data for completed matches
    """
    
    # Match Information
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name='fixtures',
        db_column='league_id'
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name='fixtures',
        db_column='season_id'
    )
    home_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='home_fixtures',
        db_column='home_team_id'
    )
    away_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='away_fixtures',
        db_column='away_team_id'
    )
    
    # Match Details
    match_date = models.DateTimeField()
    round = models.CharField(max_length=50, blank=True)
    venue = models.CharField(max_length=200, blank=True)
    
    # Match Status
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PLAY', 'In Play'),
        ('FINISHED', 'Finished'),
        ('POSTPONED', 'Postponed'),
        ('CANCELLED', 'Cancelled'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SCHEDULED'
    )
    
    # Match Results (null for scheduled matches)
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    home_halftime_score = models.IntegerField(null=True, blank=True)
    away_halftime_score = models.IntegerField(null=True, blank=True)
    
    # Expected Goals (xG) - Only for Tier 1 leagues, finished matches
    home_xg = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True
    )
    away_xg = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # API Reference
    api_fixture_id = models.CharField(max_length=50, unique=True)
    
    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'fixtures'
        verbose_name = 'Fixture'
        verbose_name_plural = 'Fixtures'
        ordering = ['match_date']
        indexes = [
            models.Index(fields=['match_date', 'league']),
            models.Index(fields=['status']),
            models.Index(fields=['home_team', 'match_date']),
            models.Index(fields=['away_team', 'match_date']),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(home_team=models.F('away_team')),
                name='different_teams'
            )
        ]
    
    def __str__(self):
        if self.status == 'FINISHED':
            return (
                f"{self.home_team.name} {self.home_score}-{self.away_score} "
                f"{self.away_team.name} ({self.match_date.date()})"
            )
        return (
            f"{self.home_team.name} vs {self.away_team.name} "
            f"({self.match_date.date()})"
        )
    
    @property
    def is_finished(self):
        return self.status == 'FINISHED'
    
    @property
    def is_upcoming(self):
        return (
            self.status == 'SCHEDULED' and 
            self.match_date > timezone.now()
        )
    
    @property
    def result(self):
        """Get match result from home team perspective."""
        if not self.is_finished or self.home_score is None:
            return None
        
        if self.home_score > self.away_score:
            return 'W'
        elif self.home_score < self.away_score:
            return 'L'
        else:
            return 'D'
    
    @property
    def total_goals(self):
        if self.home_score is not None and self.away_score is not None:
            return self.home_score + self.away_score
        return None
    
    @property
    def has_xg_data(self):
        return self.home_xg is not None and self.away_xg is not None


class Match(models.Model):
    """Match model (keeping for backwards compatibility)."""
    
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
        verbose_name=_('league'),
        db_column='league_id'
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
        verbose_name=_('home team'),
        db_column='home_team_id'
    )
    
    away_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='away_matches',
        verbose_name=_('away team'),
        db_column='away_team_id'
    )
    
    match_date = models.DateTimeField(_('match date'))
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    home_score = models.IntegerField(_('home score'), blank=True, null=True, validators=[MinValueValidator(0)])
    away_score = models.IntegerField(_('away score'), blank=True, null=True, validators=[MinValueValidator(0)])
    venue = models.CharField(_('venue'), max_length=200, blank=True, null=True)
    referee = models.CharField(_('referee'), max_length=100, blank=True, null=True)
    statistics = models.JSONField(_('statistics'), default=dict, blank=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'matches'
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
        return self.status == self.Status.FINISHED
    
    @property
    def is_live(self):
        return self.status == self.Status.LIVE


class Prediction(models.Model):
    """Prediction model."""
    
    class PredictionType(models.TextChoices):
        USER = 'USER', _('User Prediction')
        ML_MODEL = 'ML_MODEL', _('ML Model Prediction')
        STATISTICAL = 'STATISTICAL', _('Statistical Analysis')
    
    match = models.ForeignKey(
        Match, 
        on_delete=models.CASCADE, 
        related_name='predictions',
        db_column='match_id'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='predictions', 
        blank=True, 
        null=True,
        db_column='user_id'
    )
    prediction_type = models.CharField(_('prediction type'), max_length=20, choices=PredictionType.choices, default=PredictionType.USER)
    predicted_home_score = models.IntegerField(_('predicted home score'), validators=[MinValueValidator(0)])
    predicted_away_score = models.IntegerField(_('predicted away score'), validators=[MinValueValidator(0)])
    confidence = models.FloatField(_('confidence'), validators=[MinValueValidator(0), MaxValueValidator(100)])
    reasoning = models.TextField(_('reasoning'), blank=True, null=True)
    is_correct = models.BooleanField(_('is correct'), blank=True, null=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'predictions'
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
        if self.predicted_home_score > self.predicted_away_score:
            return 'HOME'
        elif self.predicted_away_score > self.predicted_home_score:
            return 'AWAY'
        return 'DRAW'
