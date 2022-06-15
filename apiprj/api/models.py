from django.db import models

from datetime import datetime

# Create your models here.


class PriceData(models.Model):
    market = models.CharField(max_length=255)
    date = models.DateTimeField(null=True)
    opening_price = models.FloatField(null=True)
    high_price = models.FloatField(null=True)
    low_price = models.FloatField(null=True)
    trade_price = models.FloatField(null=True)


class OrderbookData(models.Model):
    market = models.CharField(max_length=255)
    timestamp = models.BigIntegerField(null=True)
    ask_price = models.FloatField(null=True)
    bid_price = models.FloatField(null=True)