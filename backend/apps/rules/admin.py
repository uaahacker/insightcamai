from django.contrib import admin
from .models import Rule, RuleExecution


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'camera', 'condition', 'is_enabled', 'created_at')
    list_filter = ('condition', 'is_enabled', 'created_at')
    search_fields = ('name', 'organization__name')


@admin.register(RuleExecution)
class RuleExecutionAdmin(admin.ModelAdmin):
    list_display = ('rule', 'triggered_at')
    list_filter = ('triggered_at',)
    search_fields = ('rule__name',)
    readonly_fields = ('triggered_at',)
