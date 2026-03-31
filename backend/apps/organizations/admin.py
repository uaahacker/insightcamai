from django.contrib import admin
from .models import Organization, OrganizationMembership, OrganizationInvitation, Site


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'plan', 'created_at')
    list_filter = ('plan', 'created_at')
    search_fields = ('name', 'slug')
    readonly_fields = ('slug', 'created_at', 'updated_at')


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'organization')
    search_fields = ('user__email', 'organization__name')


@admin.register(OrganizationInvitation)
class OrganizationInvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'organization', 'role', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('email', 'organization__name')


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'location')
    list_filter = ('organization',)
    search_fields = ('name', 'location')
