"""
Data source models for the sPre application.

This module defines models for tracking data sources and sync operations.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class DataSource(models.Model):
    """
    Data source model.
    
    Represents external data sources and APIs.
    
    Attributes:
        name (CharField): Data source name
        api_url (URLField): Base API URL
        api_key_name (CharField): Environment variable name for API key
        is_active (BooleanField): Whether source is active
        rate_limit (IntegerField): Requests per minute limit
        last_sync (DateTimeField): Last successful sync timestamp
    """
    
    class SourceType(models.TextChoices):
        FOOTBALL_API = 'FOOTBALL_API', _('Football API')
        ODDS_API = 'ODDS_API', _('Odds API')
        SPORTS_DATA = 'SPORTS_DATA', _('Sports Data API')
        CUSTOM = 'CUSTOM', _('Custom Source')
    
    name = models.CharField(
        _('name'),
        max_length=100,
        unique=True,
        help_text=_('Data source name')
    )
    
    source_type = models.CharField(
        _('source type'),
        max_length=20,
        choices=SourceType.choices,
        help_text=_('Type of data source')
    )
    
    api_url = models.URLField(
        _('API URL'),
        help_text=_('Base URL for the API')
    )
    
    api_key_name = models.CharField(
        _('API key environment variable'),
        max_length=100,
        help_text=_('Name of environment variable containing API key')
    )
    
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_('Whether this data source is active')
    )
    
    rate_limit = models.IntegerField(
        _('rate limit'),
        default=60,
        help_text=_('Maximum requests per minute')
    )
    
    last_sync = models.DateTimeField(
        _('last sync'),
        blank=True,
        null=True,
        help_text=_('Timestamp of last successful sync')
    )
    
    config = models.JSONField(
        _('configuration'),
        default=dict,
        blank=True,
        help_text=_('Additional configuration options')
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('data source')
        verbose_name_plural = _('data sources')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class SyncLog(models.Model):
    """
    Sync log model.
    
    Tracks data synchronization operations.
    
    Attributes:
        data_source (ForeignKey): Related data source
        status (CharField): Sync operation status
        started_at (DateTimeField): When sync started
        completed_at (DateTimeField): When sync completed
        records_created (IntegerField): Number of records created
        records_updated (IntegerField): Number of records updated
        error_message (TextField): Error message if sync failed
    """
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')
    
    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.CASCADE,
        related_name='sync_logs',
        verbose_name=_('data source')
    )
    
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text=_('Sync operation status')
    )
    
    started_at = models.DateTimeField(
        _('started at'),
        auto_now_add=True,
        help_text=_('When sync operation started')
    )
    
    completed_at = models.DateTimeField(
        _('completed at'),
        blank=True,
        null=True,
        help_text=_('When sync operation completed')
    )
    
    records_created = models.IntegerField(
        _('records created'),
        default=0,
        help_text=_('Number of new records created')
    )
    
    records_updated = models.IntegerField(
        _('records updated'),
        default=0,
        help_text=_('Number of existing records updated')
    )
    
    error_message = models.TextField(
        _('error message'),
        blank=True,
        null=True,
        help_text=_('Error message if sync failed')
    )
    
    details = models.JSONField(
        _('details'),
        default=dict,
        blank=True,
        help_text=_('Additional sync operation details')
    )
    
    class Meta:
        verbose_name = _('sync log')
        verbose_name_plural = _('sync logs')
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['data_source', 'status']),
            models.Index(fields=['started_at']),
        ]
    
    def __str__(self):
        return f"{self.data_source.name} - {self.status} ({self.started_at})"
    
    @property
    def duration(self):
        """Calculate sync duration."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
