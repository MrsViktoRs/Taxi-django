from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
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


class StocksDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Stocks.objects.all()
    serializer_class = StockSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return JsonResponse({"errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        return JsonResponse(serializer.data)
