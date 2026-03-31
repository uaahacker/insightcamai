from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import NotificationChannel, NotificationDelivery
from .serializers import NotificationChannelSerializer, NotificationDeliverySerializer


class NotificationChannelViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationChannelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        org_slug = self.request.query_params.get('organization')
        if org_slug:
            from apps.organizations.models import Organization
            org = Organization.objects.filter(slug=org_slug).first()
            if org and org.members.filter(user=self.request.user).exists():
                return NotificationChannel.objects.filter(organization=org)
        return NotificationChannel.objects.none()
    
    def perform_create(self, serializer):
        org_slug = self.request.query_params.get('organization')
        from apps.organizations.models import Organization
        org = Organization.objects.get(slug=org_slug)
        serializer.save(organization=org)


class NotificationDeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationDeliverySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        org_slug = self.request.query_params.get('organization')
        if org_slug:
            from apps.organizations.models import Organization
            org = Organization.objects.filter(slug=org_slug).first()
            if org and org.members.filter(user=self.request.user).exists():
                return NotificationDelivery.objects.filter(channel__organization=org)
        return NotificationDelivery.objects.none()
    
    @action(detail=False, methods=['get'])
    def failed(self, request):
        """Get failed deliveries"""
        deliveries = self.get_queryset().filter(status='failed')[:50]
        serializer = self.get_serializer(deliveries, many=True)
        return Response(serializer.data)
