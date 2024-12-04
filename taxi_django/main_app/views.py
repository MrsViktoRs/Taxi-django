from time import perf_counter

import requests
import json
import os
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
            user = Users.objects.filter(res_status=True, auth_status=False)
            serializer = UserSerializer(user, many=True)
            return JsonResponse(serializer.data, safe=False)
        except Users.DoesNotExist:
            return JsonResponse({'status': 'not_found'}, status=404)


class SendMessageView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Получаем чат id и отправляем запрос
            data = json.loads(request.body)
            chat_id = data.get('chat_id')
            message = 'Ваша заявка на регистрацию отправлена.'
            url = f'https://api.telegram.org/bot{os.getenv("BOT_TOKEN")}/sendMessage'
            payload = {
                'chat_id': chat_id,
                'text': message
            }
            response = requests.post(url, json=payload)

            if response.status_code == 200:
                # После отправки сообщение добавляем message_id в БД
                user = Users.objects.filter(chat_id=chat_id).first()
                json_answer = response.json()
                message_id = json_answer['result']['message_id']
                Messages.objects.create(
                    user_id=user.id,
                    message_id=message_id,
                )
                return JsonResponse({'status': 'Message send successfully!'})
            else:
                return JsonResponse({'error': 'Failed to send message.'}, status=response.status_code)
        except Exception as err:
            print(err)


class DeleteMessageView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Получаем чат id
            data = json.loads(request.body)
            chat_id = data.get('chat_id')
            # Находим юзера
            user = Users.objects.filter(chat_id=chat_id).first()
            if not user:
                return JsonResponse({'error': 'User not found'}, status=404)
            # Меняем статус
            user.auth_status = True
            user.save()
            # Находим и удаляем старое сообщение
            message = Messages.objects.filter(user_id=user.id).first()
            if not message:
                return JsonResponse({'error': 'Message for delete not found'}, status=404)
            else:
                url = f'https://api.telegram.org/bot{os.getenv("BOT_TOKEN")}/deleteMessage'
                payload = {
                    'chat_id': chat_id,
                    'message_id': message.message_id
                }
                response_del_mess = requests.post(url, data=payload)
                if response_del_mess.status_code == 200:
                    message.delete()

            # Отправляем новое сообщение с клавиатурой и записыаем message_id в БД
            url_accep_mess = f'https://api.telegram.org/bot{os.getenv("BOT_TOKEN")}/sendMessage'
            text = ('Таксопарк “Экспансия” представлен в других соц.сетях.\n'
                    'Наш канал в Telegram{}💬 где мы регулярно публикуем новости из мира автомобилей.\n'
                    'Наш канал на YouTube{}📹 и VkVideo{} 🎞 где мы публикуем развлекательный и информативный контент.\n'
                    'Будь в теме с “Экспансией”!')
            payload_accep_mess = {
                "chat_id": chat_id,
                "text": text,
                "reply_markup": {
                    "inline_keyboard":
                        [
                            [{"text": "Смена", "callback_data": "shift"}],
                            [{"text": "Бонусы и акции", "callback_data": "bonus"}],
                            [{"text": "Твоя статистика", "callback_data": "my_stats"}, {"text": "Управление профилем", "callback_data": "profile"}],
                            [{"text": "Информация о парке", "callback_data": "info_park"}, {"text": "Связь с нами", "callback_data": "call_for"}],
                        ]
                }
            }
            response_accep_mess = requests.post(url_accep_mess, json=payload_accep_mess)
            if response_accep_mess.status_code == 200:
                res_accep_mess_json = response_accep_mess.json()
                Messages.objects.create(
                    user_id=user.id,
                    message_id=res_accep_mess_json['result']['message_id'],
                )
                return JsonResponse({'status': 'Message deleted successfully and send new message!'}, status=200)
            else:
                return JsonResponse({'error': 'New message not send.'}, status=response_accep_mess.status_code)

        except Exception as err:
            print(err)