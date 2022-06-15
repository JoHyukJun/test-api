from django.shortcuts import render
from django.http import JsonResponse

from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

import requests, json, datetime, sys, os

from datetime import datetime, timedelta

from .models import PriceData, OrderbookData
from .serializer import PriceDataSerializer, OrderbookDataSerializer

# Create your views here.


SERVER_TIME = datetime.today().strftime('%Y-%m-%d')
DATE_LIST = []


def date_range(start, end):
    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    dates = [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end-start).days+1)]
    return dates


class BitcoinPrice(APIView):
    def url_conf(self, date_list):
        url_list = []

        for d in date_list:
            tmp_url = "https://api.upbit.com/v1/candles/days?market=KRW-BTC&to=" + d + "T09%3A00%3A00Z&count=1"
            
            url_list.append(tmp_url)

        return url_list


    def request_orderbook_data(self):
        '''
            orderbook data request.
        '''
        btc_orderbook_data = OrderbookData.objects.all()
        orderbook_serializer_class = OrderbookDataSerializer(btc_orderbook_data, many=True)

        upbit_ord_url = "https://api.upbit.com/v1/orderbook?markets=KRW-BTC"

        while True:
            try:
                upbit_ord_req_data = requests.get(upbit_ord_url)
                upbit_ord_api_data = json.loads(upbit_ord_req_data.text)

                break
            except:
                pass

        upbit_ord_srz_data = {
            'market': upbit_ord_api_data[0]['market'],
            'timestamp': upbit_ord_api_data[0]['timestamp'],
            'ask_price': upbit_ord_api_data[0]['orderbook_units'][0]['ask_price'],
            'bid_price': upbit_ord_api_data[0]['orderbook_units'][0]['bid_price']
        }

        ord_srz = OrderbookDataSerializer(data=upbit_ord_srz_data)

        if ord_srz.is_valid():
            ord_srz.save()

        return


    def get(self, requset):
        '''
            GET /
            open api data call and save.
        '''
        global SERVER_TIME
        global DATE_LIST

        btc_price_data = PriceData.objects.all()
        serializer_class = PriceDataSerializer(btc_price_data, many=True)

        btc_orderbook_data = OrderbookData.objects.all()
        orderbook_serializer_class = OrderbookDataSerializer(btc_orderbook_data, many=True)

        '''
           candle data requset
        '''
        SERVER_TIME = datetime.today().strftime('%Y-%m-%d')

        if not DATE_LIST or SERVER_TIME != DATE_LIST[-1]:
            print('init')
            if not DATE_LIST:
                DATE_LIST = date_range((datetime.today() - timedelta(30)).strftime("%Y-%m-%d"), SERVER_TIME)
            else:
                DATE_LIST = []
                DATE_LIST.append(SERVER_TIME)

            url_list = self.url_conf(DATE_LIST)

            btc_price_data.delete() # test

            api_data = []

            for url in url_list:
                while True:
                    try:
                        req_data = requests.get(url)
                        api_data.append(json.loads(req_data.text))

                        break
                    except:
                        pass

            for ad in api_data:
                srl_data = {
                            'market': ad[0]['market'],
                            'date': datetime.strptime(ad[0]['candle_date_time_kst'][:10], '%Y-%m-%d'),
                            'opening_price': ad[0]['opening_price'],
                            'high_price': ad[0]['high_price'],
                            'low_price': ad[0]['low_price'],
                            'trade_price': ad[0]['trade_price'],
                            #'orderbook': ''
                        }

                srz = PriceDataSerializer(data=srl_data)

                if srz.is_valid():
                    srz.save()

                #print(srz.errors)

        # real-time orderbook data request 
        self.request_orderbook_data()

        content = {
        'candle_data': serializer_class.data,
        'orderbook_data': orderbook_serializer_class.data
        }
                
        return Response(content, status=200)
    

    @swagger_auto_schema(
        responses={200: PriceDataSerializer(many=True)})
    def post(self, request):
        '''
            POST // request json
            :param:
                {
                    "startdate": string($date-time) // ex. YYYY-MM-DD
                    "enddate": null or string($date-time)
                }
            :return:
                {
                    "candle_data": ...
                    "orderbook_data": ... (latest)
                }
        '''
        date_requset = request.data

        if not date_requset or not date_requset['startdate']:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if date_requset['enddate']:
            start_date = date_requset['startdate']
            end_date = date_requset['enddate']

            #start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')

        else:
            start_date = date_requset['startdate']
            end_date = date_requset['startdate']

            #start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')


        btc_price_data = PriceData.objects.filter(date__range=[start_date + 'T00:00:00', end_date + 'T00:00:00'])
        serializer_class = PriceDataSerializer(btc_price_data, many=True)

        btc_orderbook_data = OrderbookData.objects.all()
        orderbook_serializer_class = OrderbookDataSerializer(btc_orderbook_data, many=True)
        
        # real-time orderbook data request 
        self.request_orderbook_data()

        content = {
        'candle_data': serializer_class.data,
        'orderbook_data': orderbook_serializer_class.data[-1]
        }

        return Response(content, status=200)