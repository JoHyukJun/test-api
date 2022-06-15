from rest_framework import serializers
from .models import PriceData, OrderbookData


class PriceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceData
        fields = (
            'market',
            'date',
            'opening_price',
            'high_price',
            'low_price',
            'trade_price'
        )


class OrderbookDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderbookData
        fields = (
            'market',
            'timestamp',
            'ask_price',
            'bid_price'
        )