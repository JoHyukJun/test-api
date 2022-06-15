from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.views import APIView

# Create your views here.


class HealthView(APIView):
    def get(self, request, *args, **kwargs):
        '''
            server test
        '''
        return JsonResponse({"server state": True})
