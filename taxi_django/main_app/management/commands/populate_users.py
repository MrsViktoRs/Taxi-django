from copyreg import dispatch_table

from django.core.management.base import BaseCommand
from ...models import Users


class Command(BaseCommand):
    help = 'Заполняет таблицу RefKey несколькими записями'

    def handle(self, *args, **kwargs):
        ref_data = [
            {
                "chat_id": 123456789,
                "name": "Иван",
                "surname":"Иванов",
                "patronymic":"Иванович",
                "phone": 79997779977,
                "address":"@mail",
                "permission_number": "---",
                "active_stocks": "Твой таксопарк",
                "auth_status": True,
                "res_status": False,
             },
            {
                "chat_id": 1223334444,
                "name": "Прост",
                "surname":"Простов",
                "patronymic":"",
                "phone": 7921779977,
                "address":"@mail",
                "permission_number": "---",
                "active_stocks": "Кофемания",
                "auth_status": True,
                "res_status": False,
             },
            {
                "chat_id": 987654321,
                "name": "Ахрен",
                "surname": "Ахренев",
                "patronymic": "Ахренеевич",
                "phone": 79997432237,
                "address": "@mail",
                "permission_number": "---",
                "active_stocks": "Твой таксопарк",
                "auth_status": False,
                "res_status": True,
            },
        ]

        for data in ref_data:
            print(data['phone'])
            el = Users.objects.create(
                chat_id=data['chat_id'],
                name=data['name'],
                surname=data['surname'],
                patronymic=data['patronymic'],
                phone=data['phone'],
                address=data['address'],
                permission_number=data['permission_number'],
                active_stocks=data['active_stocks'],
                auth_status=data['auth_status'],
                res_status=data['res_status']
            )
            el.save()
            self.stdout.write(self.style.SUCCESS(f'Создана запись: {el.surname}'))