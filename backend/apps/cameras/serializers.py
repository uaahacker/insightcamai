from rest_framework import serializers
from .models import Camera, CameraHealthLog, Snapshot, VideoClip
from core.serializers import BaseSerializer


class SnapshotSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Snapshot
        fields = ('id', 'image', 'timestamp')


class CameraHealthLogSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = CameraHealthLog
        fields = ('status', 'latency_ms', 'error_message', 'checked_at')


class CameraSerializer(BaseSerializer):
    health_logs = CameraHealthLogSerializer(many=True, read_only=True)
    snapshots = SnapshotSerializer(many=True, read_only=True)
    site_name = serializers.CharField(source='site.name', read_only=True, allow_null=True)
    
    class Meta(BaseSerializer.Meta):
        model = Camera
        fields = ('id', 'organization', 'site', 'site_name', 'name', 'description', 'connection_type',
                  'host', 'port', 'username', 'stream_path', 'rtsp_url', 'stream_protocol',
                  'stream_profile', 'manufacturer', 'model', 'resolution', 'fps',
                  'is_enabled', 'health_status', 'last_seen', 'analytics_enabled',
                  'people_detection', 'people_counting', 'line_crossing', 'intrusion_detection',
                  'loitering_detection', 'parking_detection', 'extended_config',
                  'health_logs', 'snapshots', 'created_at', 'updated_at')
        read_only_fields = ('health_status', 'last_seen', 'health_logs', 'snapshots')
        extra_kwargs = {
            'encrypted_password': {'write_only': True},
        }


class CameraCreateUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Camera
        fields = ('name', 'description', 'connection_type', 'host', 'port', 'username',
                  'password', 'stream_path', 'rtsp_url', 'stream_protocol', 'stream_profile',
                  'manufacturer', 'model', 'resolution', 'fps', 'site', 'analytics_enabled',
                  'people_detection', 'people_counting', 'line_crossing', 'intrusion_detection',
                  'loitering_detection', 'parking_detection', 'extended_config')
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        camera = Camera(**validated_data)
        if password:
            camera.encrypt_password(password)
        camera.save()
        return camera
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.encrypt_password(password)
        return super().update(instance, validated_data)


class CameraTestConnectionSerializer(serializers.Serializer):
    connection_type = serializers.CharField()
    host = serializers.CharField()
    port = serializers.IntegerField()
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=False, allow_blank=True)
    stream_path = serializers.CharField(required=False, allow_blank=True)
    rtsp_url = serializers.CharField(required=False, allow_blank=True)
    stream_protocol = serializers.CharField(required=False, default='rtsp')


class VideoClipSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = VideoClip
        fields = ('id', 'video_file', 'start_time', 'end_time', 'duration_seconds', 'created_at')
