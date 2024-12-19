from django.core.management.base import BaseCommand
from ...models import Tariffs

class Command(BaseCommand):
    help = 'Заполняет таблицу Tariffs тарифами'

    def handle(self, *args, **kwargs):
        rules = [{'id': '3b669e4ffb4a4803a42adaf2fe1c777e',
                  'is_enabled': True,
                  'name': 'Фиксированный(СМЗ)'},
                 {'id': '78d9335fff1c40b7bb1ec9a53478287b',
                  'is_enabled': False,
                  'name': 'Тестовый'},
                 {'id': '7916d5a62e144072908900bb228b41dc',
                  'is_enabled': True,
                  'name': 'Процент(СМЗ)'},
                 {'id': '8f0ae1a24d3a413b91d118ed702b4ff5',
                  'is_enabled': True,
                  'name': 'Процент'},
                 {'id': 'b56444570d314ff6bc028b36af54f2fa',
                  'is_enabled': True,
                  'name': 'Суточный(Не забудь настроить СПИСАНИЯ!)'},
                 {'id': 'e26a3cf21acfe01198d50030487e046b',
                  'is_enabled': True,
                  'name': 'Фиксированный'}]
        for data in rules:
            tariff = Tariffs.objects.create(
                service_id=data['id'],
                is_enabled=data['is_enabled'],
                name=data['name']
            )
            tariff.save()
            self.stdout.write(self.style.SUCCESS(f'Создана запись: {tariff.name}'))