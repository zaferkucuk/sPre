"""
Views for datasources application.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import DataSource, SyncLog
from .serializers import DataSourceSerializer, SyncLogSerializer


class DataSourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for DataSource model.
    
    GET /api/datasources/sources/ - List data sources
    GET /api/datasources/sources/{id}/ - Get data source detail
    GET /api/datasources/sources/{id}/sync-logs/ - Get sync logs for source
    """
    
    queryset = DataSource.objects.filter(is_active=True)
    serializer_class = DataSourceSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['source_type', 'is_active']
    
    @action(detail=True, methods=['get'])
    def sync_logs(self, request, pk=None):
        """
        Get sync logs for a specific data source.
        
        GET /api/datasources/sources/{id}/sync-logs/
        """
        data_source = self.get_object()
        logs = SyncLog.objects.filter(data_source=data_source).order_by('-started_at')[:20]
        
        serializer = SyncLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def trigger_sync(self, request, pk=None):
        """
        Trigger a manual sync for data source.
        
        POST /api/datasources/sources/{id}/trigger-sync/
        
        Note: This is a placeholder. Actual sync logic should be implemented
        in background tasks using Celery.
        """
        data_source = self.get_object()
        
        # Create a sync log entry
        sync_log = SyncLog.objects.create(
            data_source=data_source,
            status=SyncLog.Status.PENDING
        )
        
        # TODO: Trigger actual sync task using Celery
        # from .tasks import sync_data_source
        # sync_data_source.delay(sync_log.id)
        
        return Response({
            'message': 'Sync triggered successfully',
            'sync_log_id': sync_log.id
        }, status=status.HTTP_202_ACCEPTED)


class SyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for SyncLog model.
    
    GET /api/datasources/sync-logs/ - List sync logs
    GET /api/datasources/sync-logs/{id}/ - Get sync log detail
    """
    
    queryset = SyncLog.objects.select_related('data_source').all()
    serializer_class = SyncLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['data_source', 'status']
    ordering = ['-started_at']
