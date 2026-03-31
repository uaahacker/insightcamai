from rest_framework import serializers
from .models import SubscriptionPlan, Subscription
from core.serializers import BaseSerializer


class SubscriptionPlanSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = SubscriptionPlan
        fields = ('id', 'name', 'slug', 'description', 'price_monthly', 'price_annual',
                  'max_cameras', 'max_users', 'features', 'created_at')


class SubscriptionSerializer(BaseSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    
    class Meta(BaseSerializer.Meta):
        model = Subscription
        fields = ('id', 'organization', 'plan', 'plan_name', 'billing_cycle', 'status',
                  'current_period_start', 'current_period_end', 'created_at', 'updated_at')
