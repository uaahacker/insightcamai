from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import Organization, OrganizationMembership, OrganizationInvitation, Site
from .serializers import (
    OrganizationSerializer, OrganizationCreateSerializer, 
    OrganizationMembershipSerializer, OrganizationInvitationSerializer,
    SiteSerializer
)
from core.permissions import IsOrganizationAdmin


class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Organization.objects.filter(
            members__user=self.request.user,
            members__is_active=True
        ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrganizationCreateSerializer
        return OrganizationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        org = serializer.save()
        
        # Add current user as owner
        OrganizationMembership.objects.create(
            organization=org,
            user=request.user,
            role='owner'
        )
        
        return Response(
            OrganizationSerializer(org).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def members(self, request, slug=None):
        org = self.get_object()
        memberships = org.members.filter(is_active=True)
        serializer = OrganizationMembershipSerializer(memberships, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def invite_member(self, request, slug=None):
        org = self.get_object()
        
        # Check permission
        if not org.members.filter(user=request.user, role__in=['owner', 'admin']).exists():
            return Response(
                {'detail': 'You do not have permission to invite members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        email = request.data.get('email')
        role = request.data.get('role', 'viewer')
        
        if not email:
            return Response({'email': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        expires_at = timezone.now() + timedelta(days=7)
        invitation, created = OrganizationInvitation.objects.update_or_create(
            organization=org,
            email=email,
            defaults={'role': role, 'invited_by': request.user, 'expires_at': expires_at, 'status': 'pending'}
        )
        
        serializer = OrganizationInvitationSerializer(invitation)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def remove_member(self, request, slug=None):
        org = self.get_object()
        
        # Check permission
        if not org.members.filter(user=request.user, role__in=['owner', 'admin']).exists():
            return Response(
                {'detail': 'You do not have permission to remove members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        membership = org.members.filter(user_id=user_id).first()
        
        if not membership:
            return Response({'detail': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)
        
        membership.is_active = False
        membership.save()
        
        return Response({'detail': 'Member removed successfully'})


class SiteViewSet(viewsets.ModelViewSet):
    serializer_class = SiteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        org_slug = self.request.query_params.get('organization')
        if org_slug:
            return Site.objects.filter(organization__slug=org_slug)
        return Site.objects.none()
    
    def perform_create(self, serializer):
        org_slug = self.request.query_params.get('organization')
        org = Organization.objects.get(slug=org_slug)
        serializer.save(organization=org)
