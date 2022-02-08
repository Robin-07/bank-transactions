from rest_framework import serializers
from django.db import connection
from .utils import check_account_exists, validate_account_no, validate_amount, check_unwanted_transfer, update_balance
import datetime

cursor = connection.cursor()

'''
    For both Serializers, validation of the incoming request data has 
    been handled by overriding the serializer class' "to_internal_value"
    method.

    The data returned by this method is available as the serializer's
    validated_data.

    The "create" method handles the database operations after receiving
    the validated data.
'''

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
        create_account_query = '''
        INSERT INTO transactions_Balance (account_no, balance) 
        VALUES (%s, %s)
        '''
        cursor.execute(create_account_query, 
        [validated_data['account_no'], validated_data['balance']])

        response = {"account_no" : validated_data['account_no']}

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

            if not errors['errors'] and from_acc_no == to_acc_no:
                errors['errors'].update({ 'Transfer Failure' : 'from and to must be different accounts' })
            
            sender_balance = check_account_exists(from_acc_no, 'from', True, cursor, errors)
            receiver_balance = check_account_exists(to_acc_no, 'to', True, cursor, errors)

            if not errors['errors']:
                if sender_balance[0] < amount: 
                    errors['errors'].update({'amount' : 'Insufficient Funds'})
                else:
                    check_unwanted_transfer(from_acc_no, datetime.datetime.now(), cursor, errors)
        
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

        create_transaction_query = '''
        INSERT INTO transactions_Transaction (account_no, amount, created_datetime) 
        VALUES (%s, %s, %s)
        '''
        cursor.execute(create_transaction_query, [sender['id'], amount, created_datetime])

        get_last_transaction_query = 'SELECT max(id) FROM transactions_Transaction'
        cursor.execute(get_last_transaction_query)
        transaction_id = cursor.fetchone()[0]

        update_balance(sender['balance'], sender['id'], cursor)
        update_balance(receiver['balance'], receiver['id'], cursor)
        
        response = { 'id' : transaction_id }
        response.update(validated_data)
        response.update({ 'created_datetime' : created_datetime })
        
        return response