import logging
import requests
import json
import os
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.db.models import Q
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .models import Users, UserCredentials
from .serializers import *

logger = logging.getLogger(__name__)


class CreateAdminView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = make_password(request.data.get('password'))
        try:
            UserCredentials.objects.create(username=username, password=password)
        except Exception as err:
            logger.error(err)
            return JsonResponse(f'username already exists', safe=False, status=HTTP_409_CONFLICT)

        return JsonResponse(f"Create amdin", safe=False, status=HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        data = request.data['regData']
        try:
            credentials = UserCredentials.objects.get(username=data['username'])
            if credentials.check_password(data['password']):
                access_token = AccessToken.for_user(credentials)
                return Response({'token': str(access_token)}, status=200)
            else:
                return Response({'error': 'Invalid credentials'}, status=400)
        except UserCredentials.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)


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
        phone = self.request.query_params.get('phone', None)

        if name:
            queryset = queryset.filter(name__icontains=name)

        if phone:
            queryset = queryset.filter(user__phone__icontains=phone)

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
    serializer_class = AppealsSerializer

    def get_queryset(self):
        query = self.request.query_params.get('search', None)
        queryset = Appeals.objects.filter(status=False).order_by('-dt')

        if query:
            queryset = queryset.filter(
                Q(user__name__icontains=query) |  # Поиск по имени
                Q(user__surname__icontains=query) |  # Поиск по фамилии
                Q(user__patronymic__icontains=query)  # Поиск по отчеству
            )

        return queryset

class AppealsView(generics.UpdateAPIView):
    serializer_class = AppealsSerializer

    def update(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        try:
            appeal = Appeals.objects.get(id=id)
            appeal.status = False
            appeal.save()
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
            data = json.loads(request.body)
            chat_id = data['chat_id']
            name = data['name']
            surname = data['surname']
            patronymic = data['patronymic']
            user = Users.objects.filter(chat_id=chat_id).first()
            if not user:
                return JsonResponse({'error': 'User not found'}, status=404)
            role = Role.objects.filter(user_id=user.id).first()
            if not role:
                logger.warning(f'request: /accept_message/ \nstatus: role is {role}')
                return JsonResponse({"error": "Role not found"}, status=403, safe=False)
            message = Messages.objects.filter(user_id=user.id).all()
            user.name = name
            user.surname = surname
            user.patronymic = patronymic
            user.auth_status = True
            user.save()
            if len(message) != 0:
                url = f'https://api.telegram.org/bot{os.getenv("BOT_TOKEN")}/deleteMessage'
                for mess in message:
                    payload = {
                        'chat_id': chat_id,
                        'message_id': mess.message_id
                    }
                    response_del_mess = requests.post(url, data=payload)
                    if response_del_mess.status_code != 200:
                        logger.warning(f'Сообщение не удалено, статус Telegram: {response_del_mess.status_code}')
                        mess.delete()
                    else:
                        mess.delete()
            else:
                logger.warning('Сообщений для удаления нет')
            url_accep_mess = f'https://api.telegram.org/bot{os.getenv("BOT_TOKEN")}/sendMessage'
            if role.name == 'driver':
                text = ("А ты смотрел видео «Экспансии» в соц.сетях❓❗️\n"
                        "Наш канал в [Telegram](t.me/ExpansiyaTaxi)💬 где мы регулярно публикуем новости из мира автомобилей.\n\n"
                        "Наши каналы на \n"
                        "📹 [YouTube](youtube.com/@ExpanciaTaxi)\n"
                        "🌐 [VkVideo](vk.com/expansiyataxi)\n"
                        "📷 [Instagram](instagram.com/expansion_taxi)\n"
                        "🕺 [Tik-Tok](tiktok.com/@expansion_taxi)\n"
                        "где мы публикуем развлекательный и информативный контент.\n"
                        "Будь в теме с «Экспансией» !")
                payload_accep_mess = {
                    "chat_id": chat_id,
                    "text": text,
                    'parse_mode': 'Markdown',
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
            elif role.name == 'partner':
                text = (
                    "Добро пожаловать в таксопарк Экспансия✋.\n"
                    "С нами не обязательно быть водителем🚘 чтобы зарабатывать!\n"
                    "Мы делимся своим доходом💰 с вами, за каждого друга, который работает в нашем парке и выполняет заказы, вы будете получать 50% от комиссии парка.\n"
                    "Подробные условия:\n"
                    "Получай по 2₽💰 с каждого заказа своего друга или👬 1₽ если он самозанятый.\n"
                    "Начисления будут действовать в течении 3х месяцев с момента первого заказа.\n"
                    "Начисления приходят один раз в месяц в период с 1-5 число следующего месяца(за исключением выходных).\n"
                    "Узнать подробную статистику по своему профилю ты можешь по кнопке “Статистика”👇)\n"
                )
                payload_accep_mess = {
                    "chat_id": chat_id,
                    "text": text,
                    'parse_mode': 'Markdown',
                    "reply_markup": {
                        "inline_keyboard":
                            [
                                [{"text": "Профиль партнера", "callback_data": "profile_parther"}],
                                [{"text": "Статистика по акциям", "callback_data": "stats_action"}],
                                [{"text": "Информация о парке", "callback_data": "info_park"}],
                                [{"text": "Связь с нами", "callback_data": "call_for"}],
                            ]
                    }
                }
                response_accep_mess = requests.post(url_accep_mess, json=payload_accep_mess)
            else:
                logger.warning(f'Нет такой роли\nUser: \nid: {user.id} \nchat_id:{user.chat_id} \nphone: {user.phone}')
                return JsonResponse({'status': 'role is not found'}, status=403)
            if response_accep_mess.status_code == 200:
                res_accep_mess_json = response_accep_mess.json()
                Messages.objects.create(
                    user_id=user.id,
                    message_id=res_accep_mess_json['result']['message_id'],
                )
                return JsonResponse({'status': 'Message deleted successfully and send new message!'}, status=200)
            else:
                return JsonResponse({'error': 'New message not send.'}, status=404)

        except Exception as err:
            logger.error(err)
            print(err)
            return JsonResponse({'error': 'exception'}, status=405)


class UserRetrieveView(APIView):
    def get(self, request, phone):
        try:
            user = Users.objects.get(phone=phone)
            serializer = UserSerializer(user)

            return JsonResponse(serializer.data, status=status.HTTP_200_OK)

        except Users.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, phone):
        try:
            user = Users.objects.get(phone=phone)
            data = request.data
            serializer = UserSerializer(instance=user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)
            else:
                return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

        except Users.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


class UserListView(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = Users.objects.filter(res_status=True, auth_status=True)
        phone = self.request.query_params.get('phone', None)
        name = self.request.query_params.get('name', None)
        surname = self.request.query_params.get('surname', None)
        patronymic = self.request.query_params.get('patronymic', None)

        if phone:
            queryset = queryset.filter(phone=phone)
        if name:
            queryset = queryset.filter(name=name)
        if surname:
            queryset = queryset.filter(surname=surname)
        if patronymic:
            queryset = queryset.filter(patronymic=patronymic)

        return queryset


class UserDetailView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    queryset = Users.objects.filter(res_status=True, auth_status=True)


class ActiveMessageView(APIView):

    def get(self, request):
        messages = ActiveMessage.objects.all()
        serializer = ActiveMessageSerializer(messages, many=True)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)

    def post(self, request):
        serializer = ActiveMessageSerializer(data=request.data)
        if serializer.is_valid():
            whom_value = serializer.validated_data['whom']
            if whom_value == 'Всем':
                serializer.validated_data['whom'] = 'all'
            elif whom_value == 'Водителям':
                serializer.validated_data['whom'] = 'driver'
            elif whom_value == 'Партнёрам':
                serializer.validated_data['whom'] = 'partner'
            serializer.save()
            return JsonResponse('True', status=status.HTTP_201_CREATED, safe=False)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        try:
            message = ActiveMessage.objects.get(pk=pk)
            message.delete()
            return JsonResponse(data='Сообщение удалено', status=status.HTTP_204_NO_CONTENT, safe=False)
        except ActiveMessage.DoesNotExist:
            return JsonResponse(data='Сообщение не удалено', status=status.HTTP_404_NOT_FOUND, safe=False)

    def put(self, request, pk=None):
        try:
            message = ActiveMessage.objects.get(pk=pk)
            serializer = ActiveMessageSerializer(message, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)

            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ActiveMessage.DoesNotExist as err:
            return JsonResponse(err, status=status.HTTP_404_NOT_FOUND)


class PartnerListAPIView(ListAPIView):
    queryset = Users.objects.filter(auth_status=False)
    serializer_class = UserSerializer
    def get_queryset(self):
        qs = super().get_queryset()
        partner_users = qs.filter(roles__name='partner')
        return JsonResponse(partner_users, safe=False)


