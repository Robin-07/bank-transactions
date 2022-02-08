from datetime import datetime


def validate_account_no(account_no, field_name, errors):
    if not account_no.isnumeric() or len(account_no) != 8:
        errors['errors'].update({ f'{field_name}' : 'account number must be numeric and 8 digits long' })

def validate_amount(value, field_name, errors):
    if not isinstance(value, int) or value < 0: 
        errors['errors'].update({ f'{field_name}' : f'{field_name} must be a non-negative integer' })

def check_account_exists(account_no, field_name, account_should_exist, cursor, errors):
    if errors['errors']:  return
    cursor.execute('''
    SELECT balance FROM transactions_Balance WHERE account_no = %s
    ''', [account_no])
    balance = cursor.fetchone()
    account_exists = balance is not None
    if account_should_exist != account_exists:
        error_msg = 'Account does not exist' if account_should_exist else 'Account already exists' 
        errors['errors'].update({ f'{field_name}' : f'{error_msg}' })
    return balance

def check_unwanted_transfer(sender_acc_no, now, cursor, errors):
    cursor.execute('''
    SELECT created_datetime FROM transactions_Transaction
    WHERE account_no = %s AND id = (SELECT max(id) FROM transactions_Transaction)
    ''', [sender_acc_no])
    last_transaction_time = cursor.fetchone()
    if last_transaction_time is not None:
        time_difference = (now - last_transaction_time[0]).total_seconds()
        if time_difference < 10:
            errors['errors'].update({ 'Transfer Failure' : 'There must be a 10 second difference between transactions' })