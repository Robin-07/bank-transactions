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