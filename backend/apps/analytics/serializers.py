from rest_framework import serializers
from .models import DailyAnalytics, HourlyAnalytics
from core.serializers import BaseSerializer


class DailyAnalyticsSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = DailyAnalytics
        fields = ('id', 'camera', 'date', 'peak_people_count', 'average_people_count',
                  'total_people_entered', 'total_people_exited', 'total_events',
                  'critical_events', 'busy_hours', 'created_at')


class HourlyAnalyticsSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = HourlyAnalytics
        fields = ('id', 'camera', 'hour', 'people_count', 'events_count', 'created_at')
