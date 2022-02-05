from asyncio.windows_events import NULL
from rest_framework import serializers
from .models import Balance


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = '__all__'

class TransferAmountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    sender = BalanceSerializer()
    receiver = BalanceSerializer()
    transfered = serializers.IntegerField()
    created = serializers.DateTimeField()