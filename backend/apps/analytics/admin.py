from django.contrib import admin
from .models import DailyAnalytics, HourlyAnalytics


@admin.register(DailyAnalytics)
class DailyAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('camera', 'date', 'peak_people_count', 'total_events')
    list_filter = ('date', 'camera')
    search_fields = ('camera__name',)


@admin.register(HourlyAnalytics)
class HourlyAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('camera', 'hour', 'people_count')
    list_filter = ('hour', 'camera')
