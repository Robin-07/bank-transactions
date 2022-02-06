from re import T
from rest_framework import serializers
from .models import Balance, Transaction
from django.db import connection


cursor = connection.cursor()

class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = '__all__'


class BalanceObjectRelatedField(serializers.RelatedField):
    def to_internal_value(self, value):
        cursor.execute('SELECT * FROM transactions_Balance WHERE account_no = %s', [value])
        if cursor.fetchone():
            return BalanceSerializer(instance=Balance.objects.get(account_no=value)).data
        raise serializers.ValidationError('Account No. Invalid')


class TransferAmountSerializer(serializers.ModelSerializer):
    sender = BalanceObjectRelatedField(queryset=Balance.objects.all())
    receiver = BalanceObjectRelatedField(queryset=Balance.objects.all())

    class Meta:
        model = Transaction
        fields = ['amount', 'sender', 'receiver']

    def validate(self, data):
        insufficient_funds = data['sender']['balance'] < data.get('amount')
        if insufficient_funds: raise serializers.ValidationError('Insufficient Funds')
        
        return data

    def create(self, validated_data):
        pass