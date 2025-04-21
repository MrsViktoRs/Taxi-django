import os
import requests
from datetime import datetime, timedelta
from django.db.models import Q
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

    messages = ActiveMessage.objects.filter(
        Q(date_to__isnull=True) | Q(date_to__gte=current_date)
    )

    for message in messages:
        should_send = False

        if message.time:
            message_time = datetime.combine(datetime.min, message.time)
            current_time_dt = datetime.combine(datetime.min, current_time)
            time_diff = abs((current_time_dt - message_time).total_seconds())
            if time_diff <= 60:
                should_send = True
        else:
            should_send = True

        if not should_send:
            continue

        if message.whom != 'all':
            users = Users.objects.filter(auth_status=True, roles__name=message.whom)
        else:
            users = Users.objects.filter(auth_status=True)

        for user in users:
            payload = {
                "chat_id": user.chat_id,
                "text": message.message,
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "Вернуться", "callback_data": "shift"}],
                    ]
                }
            }

            try:
                response = requests.post(base_url, json=payload)
                if response.status_code == 200:
                    logger.info(f'Сообщение отправлено: {user.name} ({user.chat_id})')
                else:
                    logger.warning(f'Ошибка отправки {user.chat_id}: {response.content}')
            except Exception as e:
                logger.error(f'Ошибка при отправке: {str(e)}')

        if not message.date_to or (message.date_to == current_date and (not message.time or current_time >= message.time)):
            logger.info(f'Удаление сообщения ID {message.id} после отправки')
            message.delete()