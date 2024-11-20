from django.core.management.base import BaseCommand
from ...models import RefKey


class Command(BaseCommand):
    help = 'Заполняет таблицу RefKey несколькими записями'

    def handle(self, *args, **kwargs):
        ref_data = [
            {
                "name": "Кофемания",
                "key": "kfdwLKDlmfeodl]gyR4m"
             },
            {
                "name": "Роснефть",
                "key": "6fDLKDlffdDol]gyRFm"
            },
            {
                "name": "Кофемания",
                "key": "5fRLKsDlmfeol]gyGDwm"
            },
            {
                "name": "Ещё какой-то",
                "key": "wk1d4KDtlmf7ol]gyR4am"
            },
            {
                "name": "Почти",
                "key": "FhwbnjfdcLKdsagyR4mw"
            },
            {
                "name": "Хватит",
                "key": "wkErfgrKzDlmfeolfd]gyR4m"
            },
        ]

        for data in ref_data:
            el = RefKey.objects.create(
                name=data['name'],
                key=data['key'],
            )
            el.save()
            self.stdout.write(self.style.SUCCESS(f'Создана запись: {el.name}'))