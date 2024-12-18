import os
import requests
from datetime import datetime, timedelta
from taxi_django.celery import app
from .models import ActiveMessage, Users
import logging

logger = logging.getLogger(__name__)


@app.task
def send_messages():
    base_url = f'https://api.telegram.org/bot{os.getenv("BOT_TOKEN")}/sendMessage'
    now = datetime.now()
    current_date = now.date()
    current_time = now.time()

    messages = ActiveMessage.objects.filter(date_from__lte=current_date, date_to__gte=current_date)
    print(messages)
    if messages:
        for message in messages:
            message_time = datetime.combine(datetime.min, message.time)
            current_datetime = datetime.combine(datetime.min, current_time)
            time_diff = abs((current_datetime - message_time).total_seconds())
            if time_diff <= 60:
                if message.whom != 'all':
                    users = Users.objects.filter(auth_status=True, roles__name=message.whom)
                    print("получили юзеров")
                else:
                    users = Users.objects.filter(auth_status=True)
                for user in users:
                    payload = {
                        'chat_id': user.chat_id,
                        'text': message.message
                    }
                    response = requests.post(base_url, data=payload)

                    if response.status_code == 200:
                        logger.warning(f'Сообщение отправленно {user.name} {user.chat_id}')
                    else:
                        logger.warning(f'Сообщение не отправлено {response.content}')
                if current_date == message.date_to and current_time >= message.time:
                    message.delete()
    else:
        return