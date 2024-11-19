from rest_framework import serializers

from .models import *

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