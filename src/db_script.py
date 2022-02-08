import sqlite3

def main():
	connection = sqlite3.connect('db.sqlite3')
	cursor = connection.cursor()
	create_transaction_table = """CREATE TABLE transactions_Transaction ( 
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	account_no VARCHAR(8) NOT NULL, 
	amount INTEGER UNSIGNED NOT NULL,
	created_datetime TEXT NOT NULL);"""
	cursor.execute(create_transaction_table)
	create_balance_table = """CREATE TABLE transactions_Balance ( 
	account_no VARCHAR(8) PRIMARY KEY,
	balance INTEGER UNSIGNED NOT NULL);"""
	cursor.execute(create_balance_table)
	print('Tables added Successfully')
	connection.close()

if __name__ == '__main__':
	main()