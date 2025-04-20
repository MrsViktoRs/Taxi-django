import os
import requests
from datetime import datetime, timedelta
from taxi_django.celery import app
from .models import ActiveMessage, Users, Messages
import logging

logger = logging.getLogger(__name__)



@app.task
def send_messages():
    base_url = f'https://api.telegram.org/bot{os.getenv("BOT_TOKEN")}/sendMessage'
    now = datetime.now()
    current_date = now.date()
    current_time = now.time()

    messages = ActiveMessage.objects.filter(date_to__gte=current_date)
    if messages:
        for message in messages:

            message_time = datetime.combine(datetime.min, message.time)
            current_datetime = datetime.combine(datetime.min, current_time)
            time_diff = abs((current_datetime - message_time).total_seconds())
            if time_diff <= 60:
                if message.whom != 'all':
                    users = Users.objects.filter(auth_status=True, roles__name=message.whom)
                else:
                    users = Users.objects.filter(auth_status=True)
                for user in users:
                    payload = {
                        'chat_id': user.chat_id,
                        'text': message.message,
                        "reply_markup": {
                            "inline_keyboard":
                                [
                                    [{"text": "Вернуться", "callback_data": "shift"}],
                                ]
                        }
                    }
                    response = requests.post(base_url, data=payload)

                    if response.status_code == 200:
                        logger.warning(f'Сообщение отправлено {user.name} {user.chat_id}')
                    else:
                        logger.warning(f'Сообщение не отправлено {response.content}')
                if current_date == message.date_to and current_time >= message.time:
                    message.delete()
    else:
        messages = ActiveMessage.objects.all()
        for message in messages:
            if message.whom != 'all':
                users = Users.objects.filter(auth_status=True, roles__name=message.whom)
            else:
                users = Users.objects.filter(auth_status=True)
            _send_message_and_del(message, users, base_url)

def _send_message_and_del(message, users, base_url):
    for user in users:
        payload = {
            'chat_id': user.chat_id,
            'text': message.message,
            "reply_markup": {
                "inline_keyboard":
                    [
                        [{"text": "Вернуться", "callback_data": "main_menu"}],
                    ]
            }
        }
        response = requests.post(base_url, data=payload)

        if response.status_code == 200:
            user = Users.objects.filter(chat_id=user.chat_id).first()
            json_answer = response.json()
            message_id = json_answer['result']['message_id']
            Messages.objects.create(
                user_id=user.id,
                message_id=message_id,
            )
            logger.warning(f'Сообщение отправлено {user.name} {user.chat_id}')
        else:
            logger.warning(f'Сообщение не отправлено {response.content}')

    message.delete()