# Generated by Django 5.1.3 on 2024-12-18 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0015_refkey_count_invite'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='address',
        ),
        migrations.AlterField(
            model_name='users',
            name='card_number',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
