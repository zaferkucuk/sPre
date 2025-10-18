"""
Admin configuration for datasources application.
"""

from django.contrib import admin
from .models import DataSource, SyncLog


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    """Admin interface for DataSource model."""
    list_display = [
        'name',
        'source_type',
        'is_active',
        'rate_limit',
        'last_sync',
    ]
    list_filter = ['source_type', 'is_active', 'created_at']
    search_fields = ['name', 'api_url']
    readonly_fields = ['created_at', 'updated_at', 'last_sync']


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    """Admin interface for SyncLog model."""
    list_display = [
        'data_source',
        'status',
        'started_at',
        'completed_at',
        'records_created',
        'records_updated',
        'duration_display',
    ]
    list_filter = ['status', 'data_source', 'started_at']
    search_fields = ['data_source__name', 'error_message']
    readonly_fields = ['started_at', 'duration']
    date_hierarchy = 'started_at'
    
    def duration_display(self, obj):
        """Display sync duration."""
        duration = obj.duration
        if duration:
            return f"{duration:.2f}s"
        return "-"
    duration_display.short_description = 'Duration'
