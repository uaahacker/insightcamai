from rest_framework import serializers
from .models import Organization, OrganizationMembership, OrganizationInvitation, Site
from core.serializers import BaseSerializer


class SiteSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Site
        fields = ('id', 'name', 'location', 'coordinates', 'created_at', 'updated_at')


class OrganizationMembershipSerializer(BaseSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta(BaseSerializer.Meta):
        model = OrganizationMembership
        fields = ('id', 'user_email', 'user_name', 'role', 'is_active', 'joined_at', 'updated_at')


class OrganizationSerializer(BaseSerializer):
    members = OrganizationMembershipSerializer(many=True, read_only=True)
    sites = SiteSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta(BaseSerializer.Meta):
        model = Organization
        fields = ('id', 'name', 'slug', 'description', 'logo', 'website', 'industry',
                  'plan', 'max_cameras', 'max_users', 'owns_cameras', 'privacy_confirmed',
                  'members', 'member_count', 'sites', 'created_at', 'updated_at')
        read_only_fields = ('slug',)
    
    def get_member_count(self, obj):
        return obj.members.filter(is_active=True).count()


class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('name', 'description', 'website', 'industry', 'country', 'city',
                  'owns_cameras', 'privacy_confirmed')
    
    def validate_privacy_confirmed(self, value):
        if not value:
            raise serializers.ValidationError('You must confirm privacy and legal terms')
        return value


class OrganizationInvitationSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = OrganizationInvitation
        fields = ('id', 'email', 'role', 'status', 'created_at', 'expires_at')
