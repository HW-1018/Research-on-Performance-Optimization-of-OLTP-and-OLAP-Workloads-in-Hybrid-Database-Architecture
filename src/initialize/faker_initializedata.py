import pymysql
import random
from faker import Faker
import time

# Initialize Faker
faker = Faker()

# Connect to the SingleStore (or any MySQL-compatible) database
connection = pymysql.connect(
    host="127.0.0.1",       # Replace with your host
    user="root",            # Replace with your username
    password="4601",    # Replace with your password
    database="BANK"         # Replace with your database name
)
cursor = connection.cursor()

# Randomly generate a transaction record
def generate_transaction():
    return {
        "AccountID": faker.random_int(min=100000000, max=999999999),
        "TransactionType": random.choice(['Deposit', 'Withdrawal', 'Transfer']),
        "TransactionDate": faker.date_time_this_year().strftime('%Y-%m-%d %H:%M:%S'),
        "Amount": round(random.uniform(-5000, 5000), 2),
        "BalanceAfterTransaction": round(random.uniform(1000, 20000), 2),
        "CounterpartyAccount": faker.random_int(min=100000000, max=999999999) if random.choice([True, False]) else None,
        "Description": random.choice(['Salary Deposit', 'ATM Withdrawal', 'Online Payment']),
        "TransactionStatus": random.choice(['Completed', 'Pending', 'Failed']),
        "Fee": round(random.uniform(0, 50), 2)
    }

# Perform a random operation: INSERT, UPDATE, DELETE
def perform_random_operation():
    operation = random.choice(["INSERT", "UPDATE", "DELETE"])

    if operation == "INSERT":
        # Generate a new transaction and insert into the database
        transaction = generate_transaction()
        insert_sql = """
        INSERT INTO BankTransactions 
        (AccountID, TransactionType, TransactionDate, Amount, 
         BalanceAfterTransaction, CounterpartyAccount, Description, TransactionStatus, Fee)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            transaction["AccountID"], transaction["TransactionType"], transaction["TransactionDate"],
            transaction["Amount"], transaction["BalanceAfterTransaction"], transaction["CounterpartyAccount"],
            transaction["Description"], transaction["TransactionStatus"], transaction["Fee"]
        )
        cursor.execute(insert_sql, values)
        print(f"INSERT: {transaction}")

    elif operation == "UPDATE":
        # Update a random transaction's amount and status
        update_sql = """
        UPDATE BankTransactions
        SET Amount = %s, TransactionStatus = %s
        WHERE TransactionID = (
            SELECT TransactionID FROM BankTransactions ORDER BY RAND() LIMIT 1
        )
        """
        new_amount = round(random.uniform(-5000, 5000), 2)
        new_status = random.choice(['Completed', 'Pending', 'Failed'])
        cursor.execute(update_sql, (new_amount, new_status))
        print(f"UPDATE: Amount = {new_amount}, TransactionStatus = {new_status}")

    elif operation == "DELETE":
        # Delete a random transaction
        delete_sql = """
        DELETE FROM BankTransactions
        WHERE TransactionID = (
            SELECT TransactionID FROM BankTransactions ORDER BY RAND() LIMIT 1
        )
        """
        cursor.execute(delete_sql)
        print("DELETE: A random transaction was deleted.")

    # Commit the operation
    connection.commit()

# Continuously perform random operations with a delay
try:
    print("Starting random OLTP operations (INSERT, UPDATE, DELETE)...")
    while True:
        perform_random_operation()
        time.sleep(0.2)  # Add a 0.2-second delay between operations
except KeyboardInterrupt:
    print("Stopping operations...")
finally:
    # Close the database connection
    cursor.close()
    connection.close()
    print("Database connection closed.")
