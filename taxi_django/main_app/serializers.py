from rest_framework import serializers
import locale

from .models import *

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stocks
        fields = ['id', 'on_text', 'off_text', 'status']

    def update(self, instance, validated_data):
        on_text = validated_data.get('on_text', None)
        off_text = validated_data.get('off_text', None)
        if on_text is not None:
            if on_text == "":
                validated_data.pop('on_text', None)
        elif off_text is not None:
            if off_text == "":
                validated_data.pop('off_text', None)
        instance = super().update(instance, validated_data)
        return instance


class RefKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = RefKey
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'


class AppealsSerializer(serializers.ModelSerializer):
    formatted_dt = serializers.SerializerMethodField('get_formatted_dt')
    user = UserSerializer()

    def get_formatted_dt(self, obj):
        date = obj.dt.date()
        month = date.strftime('%B')  # Получаем название месяца
        capitalized_month = month[:1].upper() + month[1:]  # Делаем первую букву заглавной
        formatted_date = date.strftime(f"%d {capitalized_month} %Y")
        time = obj.dt.time().strftime('%H:%M')
        formatted_date = f"{time}    ||    {formatted_date} Г."
        return formatted_date

    class Meta:
        model = Appeals
        fields = ['id', 'message', 'user', 'formatted_dt', 'status', 'role']
        extra_kwargs = {'dt': {'source': 'get_formatted_dt'}}