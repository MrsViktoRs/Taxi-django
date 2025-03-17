from rest_framework import serializers
# import locale

from .models import *

# locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

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

class DriverLicensesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLicenses
        fields = '__all__'


class CarsSerializer(serializers.ModelSerializer):
    chat_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Cars
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}

    def create(self, validated_data):
        chat_id = validated_data.pop('chat_id')
        user = Users.objects.filter(chat_id=chat_id).first()
        if not user:
            raise serializers.ValidationError({'chat_id': 'Пользователь с таким chat_id не найден'})
        validated_data['user'] = user
        return super().create(validated_data)

class UsersSerializer(serializers.ModelSerializer):
    driver_license = DriverLicensesSerializer(read_only=True)  # Возвращает объект при `GET`
    driver_license_id = serializers.PrimaryKeyRelatedField(
        queryset=DriverLicenses.objects.all(), source='driver_license', write_only=True
    )
    # car = CarsSerializer(read_only=True)
    # car_id = serializers.PrimaryKeyRelatedField(
    #     queryset=Cars.objects.all(), source='car', write_only=True
    # )
    role_name = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = '__all__'
        extra_fields = ['role_name']

    def get_role_name(self, obj):
        role = obj.roles.first()
        return role.name if role else None

class UsersCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class AppealsSerializer(serializers.ModelSerializer):
    formatted_dt = serializers.SerializerMethodField('get_formatted_dt')
    user = UsersSerializer()

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


class ActiveMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiveMessage
        fields = ['date_from', 'date_to', 'time', 'whom', 'message', 'id']

    # def validate_whom(self, value):
    #     allowed_values = ['Всем', 'Водителям', 'Партнёрам']
    #     if value not in allowed_values:
    #         raise serializers.ValidationError("Поле 'whom' должно быть одним из значений: всем, водителям, партнёрам.")
    #     return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        whom_mapping = {
            'all': 'Всем',
            'partner': 'Партнёрам',
            'driver': 'Водителям'
        }
        data['whom'] = whom_mapping.get(data['whom'], data['whom'])
        return data