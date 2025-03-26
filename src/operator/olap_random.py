import pymysql
import time

# Connect to the SingleStore (or any MySQL-compatible) database
connection = pymysql.connect(
    host="127.0.0.1",       # Replace with your host
    user="root",            # Replace with your username
    password="4601",    # Replace with your password
    database="BANK"         # Replace with your database name
)
cursor = connection.cursor()

# Define the 8 fixed OLAP queries
def olap_queries():
    queries = [
        # 1. 按月匯總交易金額與手續費
        """
        SELECT DATE_FORMAT(TransactionDate, '%Y-%m') AS Month, 
               TransactionType,
               SUM(Amount) AS TotalTransactionAmount,
               SUM(Fee) AS TotalFees
        FROM BankTransactions
        GROUP BY Month, TransactionType
        ORDER BY Month ASC, TransactionType;
        """,
        # 2. 每個帳戶的總交易次數與最大交易金額
        """
        SELECT AccountID, 
               COUNT(TransactionID) AS TransactionCount,
               MAX(Amount) AS MaxTransactionAmount,
               AVG(BalanceAfterTransaction) AS AvgBalance
        FROM BankTransactions
        GROUP BY AccountID
        ORDER BY TransactionCount DESC
        LIMIT 10;
        """,
        # 3. 根據交易狀態進行匯總
        """
        SELECT TransactionStatus, 
               COUNT(*) AS TransactionCount,
               SUM(Amount) AS TotalTransactionAmount
        FROM BankTransactions
        GROUP BY TransactionStatus
        ORDER BY TransactionCount DESC;
        """,
        # 4. 每日交易數量統計
        """
        SELECT DATE(TransactionDate) AS TransactionDay, 
               COUNT(*) AS TotalTransactions,
               SUM(Amount) AS TotalAmount
        FROM BankTransactions
        GROUP BY TransactionDay
        ORDER BY TransactionDay;
        """,
        # 5. 前 10 名交易量帳戶
        """
        SELECT AccountID, 
               COUNT(TransactionID) AS TransactionCount, 
               SUM(Amount) AS TotalAmount
        FROM BankTransactions
        GROUP BY AccountID
        ORDER BY TotalAmount DESC
        LIMIT 10;
        """,
        # 6. 根據描述篩選交易
        """
        SELECT Description, 
               COUNT(*) AS TransactionCount,
               SUM(Amount) AS TotalAmount
        FROM BankTransactions
        WHERE Description LIKE '%Transfer%'
        GROUP BY Description
        ORDER BY TransactionCount DESC;
        """,
        # 7. 平均餘額按交易類型匯總
        """
        SELECT TransactionType, 
               AVG(BalanceAfterTransaction) AS AvgBalance, 
               MAX(Amount) AS MaxTransactionAmount
        FROM BankTransactions
        GROUP BY TransactionType
        ORDER BY AvgBalance DESC;
        """,
        # 8. 交易金額區間統計
        """
        SELECT CASE 
                   WHEN Amount < 100 THEN 'Low (<100)'
                   WHEN Amount BETWEEN 100 AND 1000 THEN 'Medium (100-1000)'
                   ELSE 'High (>1000)'
               END AS AmountRange,
               COUNT(*) AS TransactionCount,
               SUM(Amount) AS TotalAmount
        FROM BankTransactions
        GROUP BY AmountRange
        ORDER BY TotalAmount DESC;
        """
    ]
    return queries

# Execute OLAP queries in a loop
def execute_olap_queries(loop_count=800):
    queries = olap_queries()
    for i in range(loop_count):
        print(f"Executing OLAP queries - Loop {i+1}/{loop_count}")
        for idx, query in enumerate(queries, start=1):
            cursor.execute(query)
            results = cursor.fetchall()
            print(f"Query {idx}: Executed successfully with {len(results)} rows returned.")
        time.sleep(0.01)  # Optional delay between loops

# Main execution
try:
    execute_olap_queries(loop_count=800)
except Exception as e:
    print(f"Error occurred: {e}")
finally:
    # Close the database connection
    cursor.close()
    connection.close()
    print("Database connection closed.")