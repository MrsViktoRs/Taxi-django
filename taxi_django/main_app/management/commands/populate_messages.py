from django.core.management.base import BaseCommand
from ...models import Appeals


class Command(BaseCommand):
    help = 'Заполняет таблицу RefKey несколькими записями'

    def handle(self, *args, **kwargs):
        ref_data = [
            {
                "message": "Нужно прикурить",
                "user": 1,
                "status":True,
                "role":"help",
             },
            {
                "message": "Хочу премию!",
                "user": 3,
                "status":True,
                "role":"appeal",
             },
            {
                "message": "Как мне узнать свой номер телефона? Третий раз присылаю обращение, почему нет ответа... АУУУУУУ",
                "user": 2,
                "status":False,
                "role":"appeal",
             },
            {
                "message": "Сменить авто",
                "user": 2,
                "status":True,
                "role":"orders",
             },
            {
                "message": "Стать самозанятым",
                "user": 3,
                "status":True,
                "role":"orders",
             },
            {
                "message": "Сменить авто",
                "user": 1,
                "status":False,
                "role":"orders",
             },
        ]

        for data in ref_data:
            print(data['status'])
            el = Appeals.objects.create(
                message=data['message'],
                status=data['status'],
                role=data['role'],
                id=data['user'],
            )
            el.save()
            self.stdout.write(self.style.SUCCESS(f'Создана запись: {el.message}'))