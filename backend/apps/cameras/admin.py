from django.contrib import admin
from .models import Camera, CameraHealthLog, Snapshot, VideoClip


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'connection_type', 'health_status', 'is_enabled', 'created_at')
    list_filter = ('connection_type', 'health_status', 'is_enabled', 'created_at')
    search_fields = ('name', 'host', 'organization__name')
    readonly_fields = ('health_status', 'last_seen', 'last_health_check', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic', {'fields': ('name', 'description', 'organization', 'site')}),
        ('Connection', {'fields': ('connection_type', 'host', 'port', 'username', 'encrypted_password',
                                   'stream_path', 'rtsp_url', 'stream_protocol', 'stream_profile')}),
        ('Metadata', {'fields': ('manufacturer', 'model', 'resolution', 'fps')}),
        ('Analytics', {'fields': ('analytics_enabled', 'people_detection', 'people_counting',
                                  'line_crossing', 'intrusion_detection', 'loitering_detection',
                                  'parking_detection')}),
        ('Status', {'fields': ('is_enabled', 'health_status', 'last_seen', 'last_health_check',
                               'consecutive_failures')}),
        ('Configuration', {'fields': ('extended_config',)}),
    )


@admin.register(CameraHealthLog)
class CameraHealthLogAdmin(admin.ModelAdmin):
    list_display = ('camera', 'status', 'checked_at')
    list_filter = ('status', 'checked_at')
    search_fields = ('camera__name',)
    readonly_fields = ('checked_at',)


@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    list_display = ('camera', 'timestamp')
    list_filter = ('camera', 'timestamp')
    search_fields = ('camera__name',)


@admin.register(VideoClip)
class VideoClipAdmin(admin.ModelAdmin):
    list_display = ('camera', 'start_time', 'duration_seconds', 'created_at')
    list_filter = ('camera', 'created_at')
    search_fields = ('camera__name',)
