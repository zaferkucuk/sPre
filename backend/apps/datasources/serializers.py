"""
Serializers for datasources application.
"""

from rest_framework import serializers
from .models import DataSource, SyncLog


class DataSourceSerializer(serializers.ModelSerializer):
    """Serializer for DataSource model."""
    
    class Meta:
        model = DataSource
        fields = [
            'id',
            'name',
            'source_type',
            'api_url',
            'is_active',
            'rate_limit',
            'last_sync',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'last_sync']


class SyncLogSerializer(serializers.ModelSerializer):
    """Serializer for SyncLog model."""
    
    data_source_name = serializers.CharField(source='data_source.name', read_only=True)
    duration = serializers.FloatField(read_only=True)
    
    class Meta:
        model = SyncLog
        fields = [
            'id',
            'data_source',
            'data_source_name',
            'status',
            'started_at',
            'completed_at',
            'duration',
            'records_created',
            'records_updated',
            'error_message',
            'details',
        ]
        read_only_fields = ['id', 'started_at']
