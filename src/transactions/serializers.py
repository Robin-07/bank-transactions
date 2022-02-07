from rest_framework import serializers
from django.db import connection
import datetime

cursor = connection.cursor()

class BalanceSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        errors = { 'errors' : {} }
        field_count = len(data)
        account_no = data.get('account_no')
        balance = data.get('balance')
        if field_count != 2 or account_no is None or balance is None:
            errors['errors'].update({ 'malformed-request' : 'Payload must contain fields account_no and balance' })
        else:
            if not account_no.isnumeric() or len(account_no) != 8:
                errors['errors'].update({ 'account_no' : 'account_no must be numeric and 8 digits long' })
            if not isinstance(balance, int) or balance < 0: 
                errors['errors'].update({ 'balance' : 'balance must be a non-negative value' })
            if not errors['errors']:
                cursor.execute('''
                SELECT * FROM transactions_Balance WHERE account_no = %s
                ''', [account_no])
                account_exists = cursor.fetchone() is not None
                if account_exists: 
                    errors['errors'].update({ 'account_no' : 'Account already exists' })
        if errors['errors']:
            raise serializers.ValidationError(errors)
        response = {
            'account_no' : account_no,
            'balance' : balance
        }
        return response

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
        field_count = len(data)
        from_acc_no = data.get('from')
        to_acc_no = data.get('to')
        amount = data.get('amount')
        if field_count != 3 or from_acc_no is None or to_acc_no is None or amount is None:
            errors['errors'].update({ 'malformed-request' : 'Payload must contain fields from, to and amount' })
        else:
            if not from_acc_no.isnumeric() or len(from_acc_no) != 8:
                errors['errors'].update({ 'from' : 'account_no must be numeric and 8 digits long' })
            if not to_acc_no.isnumeric() or len(to_acc_no) != 8:
                errors['errors'].update({ 'to' : 'account_no must be numeric and 8 digits long' })
            if not isinstance(amount, int) or amount < 0: 
                errors['errors'].update({ 'amount' : 'amount must be a non-negative value' })
            if not errors['errors']:
                cursor.execute('''SELECT balance FROM transactions_Balance 
                WHERE account_no = %s''', [from_acc_no])
                sender_balance = cursor.fetchone()
                if sender_balance is None:
                    errors['errors'].update({ 'from' : 'Account does not exist' })
                cursor.execute('''SELECT balance FROM transactions_Balance 
                WHERE account_no = %s''', [to_acc_no])
                receiver_balance = cursor.fetchone()
                if receiver_balance is None:
                    errors['errors'].update({ 'to' : 'Account does not exist' })
                if not errors['errors']:
                    insufficient_funds = sender_balance[0] < amount
                    if insufficient_funds: 
                        errors['errors'].update({'amount' : 'Insufficient Funds'})
        if errors['errors']:
            raise serializers.ValidationError(errors)
        response = {
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
        return response

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