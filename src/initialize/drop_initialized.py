import pymysql
import random
from faker import Faker

# Initialize Faker
faker = Faker()

# Connect to SingleStore database
connection = pymysql.connect(
    host="127.0.0.1",       # Replace with your SingleStore host
    user="root",            # Replace with your username
    password="4601",    # Replace with your password
    database="BANK"  # Replace with your database name
)

cursor = connection.cursor()
#drop table
def droptable_function():
    print("drop Table")
    drop_sql="DROP TABLE BankTransactions"
    cursor.execute(drop_sql)
#create new table
def create_function():
    print("truncate table banktransactions")
    create_sql="""
    CREATE TABLE BankTransactions (
    TransactionID INT AUTO_INCREMENT PRIMARY KEY,
    AccountID BIGINT NOT NULL,
    TransactionType VARCHAR(50),
    TransactionDate DATETIME,
    Amount DECIMAL(10,2),
    BalanceAfterTransaction DECIMAL(10,2),
    CounterpartyAccount BIGINT,
    Description VARCHAR(255),
    TransactionStatus VARCHAR(50),
    Fee DECIMAL(10,2));"""
    cursor.execute(create_sql)

# Function to generate a single transaction record (without TransactionID)
def generate_transaction():
    account_id = faker.random_int(min=100000000, max=999999999)
    transaction_type = random.choice(['Deposit', 'Withdrawal', 'Transfer', 'Payment', 'Refund'])
    transaction_date = faker.date_time_this_year()
    amount = round(random.uniform(-5000, 5000), 2)
    balance_after_transaction = round(random.uniform(1000, 20000), 2)
    counterparty_account = faker.random_int(min=100000000, max=999999999) if transaction_type in ['Transfer', 'Payment'] else None
    description = random.choice(['Salary Deposit', 'ATM Withdrawal', 'Online Payment', 'Transfer to savings', 'Utility Bill'])
    transaction_status = random.choice(['Completed', 'Pending', 'Failed'])
    fee = round(random.uniform(0, 50), 2) if transaction_type in ['Transfer', 'Withdrawal', 'Payment'] else 0.0

    return (
        account_id,
        transaction_type,
        transaction_date,
        amount,
        balance_after_transaction,
        counterparty_account,
        description,
        transaction_status,
        fee
    )

# SQL query to insert a record (TransactionID is auto-incremented in the database)
insert_sql = """
INSERT INTO BankTransactions 
(AccountID, TransactionType, TransactionDate, Amount, 
 BalanceAfterTransaction, CounterpartyAccount, Description, TransactionStatus, Fee)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
# table
droptable_function()
create_function()

# Generate and insert 100,000 records
try:
    print("Starting data generation and insertion for 100,000 records...")
    batch_size = 1000  # Insert in batches of 1000 for better performance
    for batch_start in range(0, 100000, batch_size):
        transactions = [generate_transaction() for _ in range(batch_size)]
        cursor.executemany(insert_sql, transactions)  # Batch insert
        connection.commit()
        print(f"Inserted {batch_start + batch_size} records...")
    print("Data generation and insertion complete.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Close the database connection
    cursor.close()
    connection.close()
    print("Database connection closed.")