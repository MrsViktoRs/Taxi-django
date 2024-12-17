import os
import requests
from datetime import datetime
from celery import shared_task
from .models import ActiveMessage, Users


@shared_task()
def send_messages():
    base_url = f'https://api.telegram.org/bot{os.getenv("BOT_TOKEN")}/sendMessage'
    print('задача')
    now = datetime.now()
    current_date = now.date()
    current_time = now.time()

    messages = ActiveMessage.objects.filter(date_from__lte=current_date, date_to__gte=current_date)

    for message in messages:
        if current_time >= message.time:
            if message.whom != 'all':
                users = Users.objects.filter(auth_status=True, role=message.whom)
            else:
                users = Users.objects.filter(auth_status=True)
            for user in users:
                payload = {
                    'chat_id': user.chat_id,
                    'text': message.message
                }
                response = requests.post(base_url, data=payload)
                print(response.status_code)
            if current_date == message.date_to and current_time >= message.time:
                message.delete()