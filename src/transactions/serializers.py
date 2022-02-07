from rest_framework import serializers
from .models import Balance
from django.db import connection
import datetime

cursor = connection.cursor()

class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = '__all__'


class TransferAmountSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        from_acc_no = data.get('from')
        to_acc_no = data.get('to')
        amount = data.get('amount')
        cursor.execute('''SELECT balance FROM transactions_Balance 
        WHERE account_no = %s''', [from_acc_no])
        sender_balance = cursor.fetchone()
        if sender_balance is None:
            raise serializers.ValidationError({'from' : 'Invalid Account No.'})
        cursor.execute('''SELECT balance FROM transactions_Balance 
        WHERE account_no = %s''', [to_acc_no])
        receiver_balance = cursor.fetchone()
        if receiver_balance is None:
            raise serializers.ValidationError({'to' : 'Invalid Account No.'})
        insufficient_funds = sender_balance[0] < amount
        if insufficient_funds: raise serializers.ValidationError({'amount' : 'Insufficient Funds'})
        return {
            'from' : {
                'id' : from_acc_no,
                'balance' : sender_balance[0] - amount
            },
            'to' : {
                'id' : to_acc_no,
                'balance' : receiver_balance[0] + amount
            },
            'transfered' : amount
        }

    def create(self, validated_data):
        sender = validated_data['from']
        receiver = validated_data['to']
        amount = validated_data['transfered']
        created_datetime = datetime.datetime.now()
        cursor.execute('''
        INSERT INTO transactions_Transaction (account_no, amount, created_datetime) 
        VALUES (%s, %s, %s)
        ''', [sender['id'], amount, created_datetime])
        cursor.execute('SELECT max(id) FROM transactions_Transaction')
        transaction_id = cursor.fetchone()[0]
        cursor.execute('''UPDATE transactions_Balance SET balance = %s 
        WHERE account_no = %s''', [sender['balance'], sender['id']])
        cursor.execute('''UPDATE transactions_Balance SET balance = %s 
        WHERE account_no = %s''', [receiver['balance'], receiver['id']])
        response_data = { 'id' : transaction_id }
        response_data.update(validated_data)
        response_data.update({ 'created_datetime' : created_datetime })
        return response_data