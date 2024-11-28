import requests
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from rest_framework.decorators import action

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

class RefKeyListCreateView(generics.ListCreateAPIView):
    serializer_class = RefKeySerializer

    def get_queryset(self):
        queryset = RefKey.objects.all()
        name = self.request.query_params.get('name', None)

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset

class RefKeyRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RefKey.objects.all()
    serializer_class = RefKeySerializer


@csrf_exempt
def get_messages(request):
    if request.method == 'GET':
        messages = Appeals.objects.filter(status=True).order_by('-dt')
        serializer = AppealsSerializer(messages, many=True)
        return JsonResponse(serializer.data, safe=False)

class AppealsHistoryGet(generics.ListCreateAPIView):
    queryset = Appeals.objects.filter(status=False).order_by('-dt')
    serializer_class = AppealsSerializer

class AppealsView(generics.UpdateAPIView):
    serializer_class = AppealsSerializer

    def update(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        try:
            appeal = Appeals.objects.get(id=id)  # Получаем объект Appeals по id
            appeal.status = False  # Меняем статус на False
            appeal.save()  # Сохраняем изменения
            return JsonResponse({"message": "Status updated successfully!"}, status=status.HTTP_200_OK)
        except Appeals.DoesNotExist:

            return JsonResponse({"error": "Appeal not found."}, status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
def get_user_status(request):
    if request.method == 'GET':
        try:
            user = Users.objects.filter(res_status=False)
            serializer = UserSerializer(user, many=True)
            return JsonResponse(serializer.data, safe=False)
        except Users.DoesNotExist:
            return JsonResponse({'status': 'not_found'}, status=404)


class SendMessageView(View):
    def post(self, request, *args, **kwargs):
        chat_id = request.GET.get('chat_id')
        message = 'тест'

        if not message:
            return JsonResponse({'error': 'Message content cannot be empty.'}, status=400)

        token = '7754471910:AAGJ0T8CHy6MP4CsSr-pkqU0syYAHXWeX04'
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': message
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return JsonResponse({'status': 'Message sent successfully!'})
        else:
            return JsonResponse({'error': 'Failed to send message.'}, status=response.status_code)