from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import DailyAnalytics, HourlyAnalytics
from .serializers import DailyAnalyticsSerializer, HourlyAnalyticsSerializer
from django.utils import timezone
from datetime import timedelta


class AnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        org_slug = self.request.query_params.get('organization')
        if org_slug:
            from apps.organizations.models import Organization
            org = Organization.objects.filter(slug=org_slug).first()
            if org and org.members.filter(user=self.request.user).exists():
                return DailyAnalytics.objects.filter(camera__organization=org)
        return DailyAnalytics.objects.none()
    
    def get_serializer_class(self):
        return DailyAnalyticsSerializer
    
    @action(detail=False, methods=['get'])
    def daily(self, request):
        """Get daily analytics"""
        camera_id = request.query_params.get('camera_id')
        days = int(request.query_params.get('days', 30))
        
        if camera_id:
            analytics = DailyAnalytics.objects.filter(
                camera_id=camera_id,
                date__gte=timezone.now().date() - timedelta(days=days)
            ).order_by('date')
        else:
            analytics = self.get_queryset()[:30]
        
        serializer = DailyAnalyticsSerializer(analytics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def hourly(self, request):
        """Get hourly analytics"""
        camera_id = request.query_params.get('camera_id')
        hours = int(request.query_params.get('hours', 24))
        
        if camera_id:
            analytics = HourlyAnalytics.objects.filter(
                camera_id=camera_id,
                hour__gte=timezone.now() - timedelta(hours=hours)
            ).order_by('hour')
        else:
            analytics = HourlyAnalytics.objects.all()[:24]
        
        serializer = HourlyAnalyticsSerializer(analytics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get analytics summary for organization"""
        org_slug = request.query_params.get('organization')
        from apps.organizations.models import Organization
        
        org = Organization.objects.filter(slug=org_slug).first()
        if not org or not org.members.filter(user=request.user).exists():
            return Response({'detail': 'Not found'}, status=404)
        
        today = timezone.now().date()
        today_data = DailyAnalytics.objects.filter(
            camera__organization=org,
            date=today
        )
        
        summary = {
            'total_people_today': sum(d.total_people_entered for d in today_data),
            'peak_count_today': max((d.peak_people_count for d in today_data), default=0),
            'total_events_today': sum(d.total_events for d in today_data),
            'critical_events_today': sum(d.critical_events for d in today_data),
            'camera_count': org.cameras.count(),
            'online_cameras': org.cameras.filter(health_status='online').count(),
        }
        
        return Response(summary)
