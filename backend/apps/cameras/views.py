from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Camera, CameraHealthLog, Snapshot, VideoClip
from .serializers import (
    CameraSerializer, CameraCreateUpdateSerializer,
    CameraTestConnectionSerializer, CameraHealthLogSerializer,
    VideoClipSerializer
)
from .stream_tester import StreamConnectionTester
from .tasks import test_stream_connection
from core.permissions import IsOrganizationMember


class CameraViewSet(viewsets.ModelViewSet):
    serializer_class = CameraSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        org_slug = self.request.query_params.get('organization')
        if org_slug:
            from apps.organizations.models import Organization
            org = Organization.objects.filter(slug=org_slug).first()
            if org and org.members.filter(user=self.request.user).exists():
                return Camera.objects.filter(organization=org)
        return Camera.objects.none()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CameraCreateUpdateSerializer
        elif self.action == 'test_connection':
            return CameraTestConnectionSerializer
        return CameraSerializer
    
    def perform_create(self, serializer):
        org_slug = self.request.query_params.get('organization')
        from apps.organizations.models import Organization
        org = Organization.objects.get(slug=org_slug)
        serializer.save(organization=org, created_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def test_connection(self, request):
        """Test camera stream connection before saving"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        if data['connection_type'] == 'rtsp':
            success, message = StreamConnectionTester.test_rtsp_stream(
                data['host'],
                data['port'],
                data.get('username', ''),
                data.get('password', ''),
                data.get('stream_path', ''),
                data.get('stream_protocol', 'rtsp')
            )
        elif data['connection_type'] == 'http_mjpeg':
            success, message = StreamConnectionTester.test_http_stream(
                data['host'],
                data['port'],
                data.get('stream_path', ''),
                data.get('username', ''),
                data.get('password', '')
            )
        else:
            success, message = False, "Unsupported connection type"
        
        return Response({
            'success': success,
            'message': message,
            'connection_type': data['connection_type']
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def health_logs(self, request, pk=None):
        """Get health logs for a camera"""
        camera = self.get_object()
        logs = camera.health_logs.all()[:100]
        serializer = CameraHealthLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def snapshots(self, request, pk=None):
        """Get recent snapshots for a camera"""
        camera = self.get_object()
        snapshots = camera.snapshots.all()[:20]
        serializer = SnapshotSerializer(snapshots, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def clips(self, request, pk=None):
        """Get video clips for a camera"""
        camera = self.get_object()
        clips = camera.clips.all()[:20]
        serializer = VideoClipSerializer(clips, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def enable(self, request, pk=None):
        """Enable a camera"""
        camera = self.get_object()
        camera.is_enabled = True
        camera.save(update_fields=['is_enabled'])
        return Response({'detail': 'Camera enabled'})
    
    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        """Disable a camera"""
        camera = self.get_object()
        camera.is_enabled = False
        camera.save(update_fields=['is_enabled'])
        return Response({'detail': 'Camera disabled'})
