from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SubscriptionPlan, Subscription
from .serializers import SubscriptionPlanSerializer, SubscriptionSerializer


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = []


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        org_slug = self.request.query_params.get('organization')
        if org_slug:
            from apps.organizations.models import Organization
            org = Organization.objects.filter(slug=org_slug).first()
            if org and org.members.filter(user=self.request.user).exists():
                return Subscription.objects.filter(organization=org)
        return Subscription.objects.none()
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current subscription for organization"""
        org_slug = request.query_params.get('organization')
        from apps.organizations.models import Organization
        
        org = Organization.objects.filter(slug=org_slug).first()
        if not org or not org.members.filter(user=request.user).exists():
            return Response({'detail': 'Not found'}, status=404)
        
        subscription = Subscription.objects.filter(organization=org).first()
        if subscription:
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        
        return Response({'detail': 'No subscription found'}, status=404)
