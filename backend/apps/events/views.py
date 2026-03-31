from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Event
from .serializers import EventSerializer
from django.db.models import Q


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        org_slug = self.request.query_params.get('organization')
        if org_slug:
            from apps.organizations.models import Organization
            org = Organization.objects.filter(slug=org_slug).first()
            if org and org.members.filter(user=self.request.user).exists():
                return Event.objects.filter(camera__organization=org)
        return Event.objects.none()
    
    @action(detail=False, methods=['get'])
    def unprocessed(self, request):
        """Get unprocessed events"""
        events = self.get_queryset().filter(is_processed=False).order_by('-occurred_at')[:50]
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_processed(self, request, pk=None):
        """Mark an event as processed"""
        event = self.get_object()
        event.is_processed = True
        from django.utils import timezone
        event.processed_at = timezone.now()
        event.save(update_fields=['is_processed', 'processed_at'])
        return Response({'detail': 'Event marked as processed'})
