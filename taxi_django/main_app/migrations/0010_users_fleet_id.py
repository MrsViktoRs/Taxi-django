# Generated by Django 5.1.3 on 2024-12-11 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0009_users_self_worker_verygooddriver_yourtaxipark'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='fleet_id',
            field=models.BigIntegerField(blank=True, max_length=500, null=True),
        ),
    ]