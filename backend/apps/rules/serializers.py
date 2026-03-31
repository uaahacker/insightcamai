from rest_framework import serializers
from .models import Rule, RuleExecution
from core.serializers import BaseSerializer


class RuleSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Rule
        fields = ('id', 'organization', 'camera', 'name', 'description', 'condition', 'threshold',
                  'start_time', 'end_time', 'days_of_week', 'actions', 'severity', 'cooldown_minutes',
                  'is_enabled', 'created_at', 'updated_at')


class RuleExecutionSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = RuleExecution
        fields = ('id', 'rule', 'triggered_at', 'event_data', 'actions_executed')
