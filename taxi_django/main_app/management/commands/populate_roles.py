from django.core.management.base import BaseCommand
from ...models import Role

class Command(BaseCommand):
    help = 'Заполняет таблицу Role ролями'

    def handle(self, *args, **kwargs):
        roles = [{'id': '',
                  'is_enabled': True,
                  'name': 'Фиксированный(СМЗ)'},
                 {'id': '78d9335fff1c40b7bb1ec9a53478287b',
                  'is_enabled': False,
                  'name': 'Тестовый'},
                 {'id': '7916d5a62e144072908900bb228b41dc',
                  'is_enabled': True,
                  'name': 'Процент(СМЗ)'}]
        for data in roles:
            tariff = Role.objects.create(
                serviceid=data['id'],
                is_enabled=data['is_enabled'],
                name=data['name']
            )
            tariff.save()
            self.stdout.write(self.style.SUCCESS(f'Создана запись: {tariff.name}'))