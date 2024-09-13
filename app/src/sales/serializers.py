
from rest_framework import serializers


class DailySalesStatsSerializer(serializers.Serializer):
    invoice_count = serializers.IntegerField(default=0)
    total_revenue = serializers.FloatField(default=0.0)
    average_revenue = serializers.FloatField(default=0.0)
    total_profit = serializers.FloatField(default=0.0)
    revenue_to_profit_percentage = serializers.FloatField(default=0.0)

class TopClientsSerializer(serializers.Serializer):
    id = serializers.CharField()
    label = serializers.CharField()
    value = serializers.FloatField()
