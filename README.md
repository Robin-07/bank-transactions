# bank-transactions
**An ORM less Django application that implements banking APIs**
## API Endpoints
### /account
##### POST request payload: <br /> 
```
  { 
    "account_no": "8_digit_number",
    "balance": "initial_balance" 
  }
```
**Action** : New account is created with specified balance.
### /transfer
##### POST request payload: <br /> 
```
  { 
    "from": "account_no",
    "to": "account_no",
    "amount": "transfer_amount"
  }
```
**Action** : Amount is transferred from one account to the other.
## How to Run 
**Run the following commands in the terminal**
#### 1. Use `git clone https://github.com/Robin-07/bank-transactions.git` to clone this repository.
#### 2. Inside cloned repository, use `pip install requirements.txt`
#### 3. Inside src directory, first use `python db_script.py` and then use `python manage.py runserver` to start local server.
