import pymysql
import time
import random

# 連接到 SingleStore (MySQL-compatible database)
connection = pymysql.connect(
    host="127.0.0.1",       # Replace with your host
    user="root",            # Replace with your username
    password="4601",    # Replace with your password
    database="BANK"         # Replace with your database name
)
cursor = connection.cursor()

# 定義 16 個 SQL 語句 (8 OLTP + 8 OLAP)
queries = {
    "oltp": [
        """
        INSERT INTO BankTransactions 
            (AccountID, TransactionType, TransactionDate, Amount, BalanceAfterTransaction, CounterpartyAccount, Description, TransactionStatus, Fee)
        VALUES 
            (FLOOR(RAND() * 1000000000 + 100000000), 
             CASE FLOOR(RAND() * 3) 
                 WHEN 0 THEN 'Deposit' 
                 WHEN 1 THEN 'Withdrawal' 
                 ELSE 'Transfer' 
             END, 
             NOW(), 
             ROUND(RAND() * 1000, 2), 
             ROUND(RAND() * 10000, 2), 
             IF(FLOOR(RAND() * 2) = 1, FLOOR(RAND() * 1000000000 + 100000000), NULL), 
             CONCAT('Transaction ', FLOOR(RAND() * 1000)), 
             'Completed', 
             ROUND(RAND() * 10, 2)
            );
        """,
        """
        UPDATE BankTransactions
        SET TransactionStatus = CASE FLOOR(RAND() * 2)
                                  WHEN 0 THEN 'Completed'
                                  ELSE 'Failed'
                               END
        WHERE TransactionID = FLOOR(RAND() * 1000) + 1;
        """,
        """
        DELETE FROM BankTransactions
        WHERE TransactionID = FLOOR(RAND() * 1000) + 1;
        """,
        """
        UPDATE BankTransactions
        SET Fee = ROUND(RAND() * 20, 2)
        WHERE TransactionType = 'Withdrawal' 
          AND TransactionDate >= DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 7 + 1) DAY);
        """,
        """
        INSERT INTO BankTransactions
            (AccountID, TransactionType, TransactionDate, Amount, BalanceAfterTransaction, CounterpartyAccount, Description, TransactionStatus, Fee)
        VALUES 
            (FLOOR(RAND() * 1000000000 + 100000000), 
             'Transfer', 
             NOW(), 
             ROUND(RAND() * 500, 2), 
             ROUND(RAND() * 10000, 2), 
             FLOOR(RAND() * 1000000000 + 100000000), 
             CONCAT('Transfer to Account ', FLOOR(RAND() * 1000000)), 
             'Completed', 
             ROUND(RAND() * 5, 2));
        """,
        """
        DELETE FROM BankTransactions
        WHERE TransactionStatus = 'Cancelled' 
        AND TransactionDate BETWEEN DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 10 + 1) DAY) AND NOW();
        """,
        """
        DELETE FROM BankTransactions
        WHERE TransactionID = FLOOR(RAND() * 1000) + 1;
        """,
        """
        UPDATE BankTransactions
        SET TransactionType = 'UpdatedType'
        WHERE TransactionID = FLOOR(RAND() * 1000) + 1;
        """
    ],
    "olap": [
        """
        SELECT 
            DATE_FORMAT(TransactionDate, '%Y-%m') AS Month, 
            SUM(Amount) AS TotalTransactionAmount
        FROM BankTransactions
        GROUP BY Month
        ORDER BY Month DESC;
        """,
        """
        SELECT 
            AccountID, 
            COUNT(*) AS TransactionCount, 
            SUM(Amount) AS TotalAmount
        FROM BankTransactions
        GROUP BY AccountID
        ORDER BY TotalAmount DESC
        LIMIT 5;
        """,
        """
        SELECT 
            TransactionStatus, 
            COUNT(*) AS TotalTransactions
        FROM BankTransactions
        GROUP BY TransactionStatus;
        """,
        """
        SELECT 
            DATE(TransactionDate) AS TransactionDay, 
            COUNT(*) AS TotalTransactions
        FROM BankTransactions
        GROUP BY TransactionDay
        ORDER BY TransactionDay DESC;
        """,
        """
        SELECT 
            MAX(Amount) AS MaxTransactionAmount
        FROM BankTransactions;
        """,
        """
        SELECT 
            AVG(BalanceAfterTransaction) AS AvgBalance
        FROM BankTransactions;
        """,
        """
        SELECT 
            CASE 
                WHEN Amount < 100 THEN 'Low'
                WHEN Amount BETWEEN 100 AND 500 THEN 'Medium'
                ELSE 'High'
            END AS AmountRange,
            COUNT(*) AS Transactions
        FROM BankTransactions
        GROUP BY AmountRange;
        """,
        """
        SELECT 
            Description, 
            COUNT(*) AS Total
        FROM BankTransactions
        GROUP BY Description
        ORDER BY Total DESC
        LIMIT 5;
        """
    ]
}

# 執行每次迴圈執行隨機 8 個 SQL 指令
def execute_random_queries(oltp_ratio=50):
    try:
        for loop in range(1, 10001):
            print(f"--- Loop {loop}/10000 ---")
            
            selected_queries = []
            for _ in range(8):
                if random.randint(1, 100) <= oltp_ratio:
                    selected_queries.append(random.choice(queries["oltp"]))
                else:
                    selected_queries.append(random.choice(queries["olap"]))

            for query in selected_queries:
                try:
                    cursor.execute(query)
                    if query.strip().upper().startswith("SELECT"):
                        result = cursor.fetchall()
                        print(f"Query Returned {len(result)} rows.")
                    else:
                        connection.commit()
                        print(f"Query Executed successfully.")
                except Exception as e:
                    print(f"Error executing query: {e}")

            time.sleep(0.01)  # 每次迴圈間延遲 1 秒，避免過大壓力

    except Exception as e:
        print(f"Error occurred during execution: {e}")
    finally:
        cursor.close()
        connection.close()
        print("Database connection closed.")

# 主程式執行
# 例如，OLTP:OLAP 比例為 70:30
execute_random_queries(oltp_ratio=50)