from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Rule, RuleExecution
from .serializers import RuleSerializer, RuleExecutionSerializer


class RuleViewSet(viewsets.ModelViewSet):
    serializer_class = RuleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        org_slug = self.request.query_params.get('organization')
        if org_slug:
            from apps.organizations.models import Organization
            org = Organization.objects.filter(slug=org_slug).first()
            if org and org.members.filter(user=self.request.user).exists():
                return Rule.objects.filter(organization=org)
        return Rule.objects.none()
    
    def perform_create(self, serializer):
        org_slug = self.request.query_params.get('organization')
        from apps.organizations.models import Organization
        org = Organization.objects.get(slug=org_slug)
        serializer.save(organization=org, created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def executions(self, request):
        """Get recent rule executions"""
        rule_id = request.query_params.get('rule_id')
        if rule_id:
            executions = RuleExecution.objects.filter(rule_id=rule_id)[:50]
        else:
            org_slug = request.query_params.get('organization')
            from apps.organizations.models import Organization
            org = Organization.objects.filter(slug=org_slug).first()
            if org:
                executions = RuleExecution.objects.filter(rule__organization=org)[:50]
            else:
                executions = RuleExecution.objects.none()
        
        serializer = RuleExecutionSerializer(executions, many=True)
        return Response(serializer.data)
