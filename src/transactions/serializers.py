from rest_framework import serializers
from django.db import connection
from .utils import check_account_exists, validate_account_no, validate_amount
import datetime

cursor = connection.cursor()

class BalanceSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        errors = { 'errors' : {} }
        account_no = data.get('account_no')
        balance = data.get('balance')
        if len(data) != 2 or account_no is None or balance is None:
            errors['errors'].update({ 'malformed-request' : 'Payload must contain fields account_no and balance' })
        else:
            validate_account_no(account_no, 'account_no', errors)
            validate_amount(balance, 'balance', errors)
            check_account_exists(account_no, 'account_no', False, cursor, errors)
        if errors['errors']:
            raise serializers.ValidationError(errors)
        validated_data = {
            'account_no' : account_no,
            'balance' : balance
        }
        return validated_data

    def create(self, validated_data):
        cursor.execute('''
        INSERT INTO transactions_Balance (account_no, balance) 
        VALUES (%s, %s)
        ''', [validated_data['account_no'], validated_data['balance']])
        response = {"success" : "Account Was Created"}
        return response


class TransferAmountSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        errors = { 'errors' : {} }
        from_acc_no = data.get('from')
        to_acc_no = data.get('to')
        amount = data.get('amount')
        if len(data) != 3 or from_acc_no is None or to_acc_no is None or amount is None:
            errors['errors'].update({ 'malformed-request' : 'Payload must contain fields from, to and amount' })
        else:
            validate_account_no(from_acc_no, 'from', errors)
            validate_account_no(to_acc_no, 'to', errors)
            validate_amount(amount, 'amount', errors)
            sender_balance = check_account_exists(from_acc_no, 'from', True, cursor, errors)
            receiver_balance = check_account_exists(to_acc_no, 'to', True, cursor, errors)
            if not errors['errors']:
                if sender_balance[0] < amount: 
                    errors['errors'].update({'amount' : 'Insufficient Funds'})
        if errors['errors']:
            raise serializers.ValidationError(errors)
        validated_data = {
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
        return validated_data

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
        response = { 'id' : transaction_id }
        response.update(validated_data)
        response.update({ 'created_datetime' : created_datetime })
        return response