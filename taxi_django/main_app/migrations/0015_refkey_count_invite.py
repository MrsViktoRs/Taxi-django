# Generated by Django 5.1.3 on 2024-12-18 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0014_activemessage_date_from_activemessage_date_to_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='refkey',
            name='count_invite',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
