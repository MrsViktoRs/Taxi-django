from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from django.http import JsonResponse, HttpResponse
from rest_framework.renderers import JSONRenderer
from requests import get

from .models import *
from .serializers import *

class StockView(ListAPIView):
    serializer_class = StockSerializer
    queryset = Stocks.objects.all()
