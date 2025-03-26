import pymysql
import time
import random

# 連接到 SingleStore 資料庫
connection = pymysql.connect(
    host="127.0.0.1",       # 資料庫主機
    user="root",            # 用戶名
    password="4601",        # 密碼
    database="BANK"         # 資料庫名稱
)
cursor = connection.cursor()

# 建立效能記錄表格（如果尚未存在）
cursor.execute("""
CREATE TABLE IF NOT EXISTS OLTPOLAPPerformance (
    OperationID INT AUTO_INCREMENT PRIMARY KEY,
    QueryName VARCHAR(255),
    QueryType VARCHAR(10),          -- OLTP 或 OLAP
    QueueTime DECIMAL(10, 4),       -- 佇列時間（秒）
    WaitTime DECIMAL(10, 4),        -- 等待時間（秒）
    ExecutionTime DECIMAL(10, 4),   -- 執行時間（秒）
    RowsScanned INT,                -- 數據掃描量
    Throughput DECIMAL(10, 4),      -- 吞吐量（行數/秒）
    ExecutedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 執行時間戳
);
""")
connection.commit()

# 清除記錄表格
def clear_performance_table():
    try:
        print("Clearing the OLTPOLAPPerformance table...")
        cursor.execute("TRUNCATE TABLE OLTPOLAPPerformance;")
        connection.commit()
        print("Table cleared successfully.")
    except Exception as e:
        print(f"Error while clearing table: {e}")

# 定義 OLTP 和 OLAP SQL 語句
queries = {
    "oltp": [
        ("Insert Transaction", """
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
             FLOOR(RAND() * 1000000000 + 100000000), 
             CONCAT('Transaction ', FLOOR(RAND() * 1000)), 
             'Completed', 
             ROUND(RAND() * 10, 2));
        """),
        ("Update Transaction Status", """
        UPDATE BankTransactions
        SET TransactionStatus = CASE FLOOR(RAND() * 2)
                                  WHEN 0 THEN 'Completed'
                                  ELSE 'Failed'
                               END
        WHERE TransactionID = FLOOR(RAND() * 1000) + 1;
        """),
        ("Delete Random Transaction", """
        DELETE FROM BankTransactions
        WHERE TransactionID = FLOOR(RAND() * 1000) + 1;
        """),
        ("Update Fee", """
        UPDATE BankTransactions
        SET Fee = ROUND(RAND() * 20, 2)
        WHERE TransactionType = 'Withdrawal';
        """),
        ("Insert Transfer Transaction", """
        INSERT INTO BankTransactions
            (AccountID, TransactionType, TransactionDate, Amount, BalanceAfterTransaction, CounterpartyAccount, Description, TransactionStatus, Fee)
        VALUES 
            (FLOOR(RAND() * 1000000000 + 100000000), 
             'Transfer', NOW(), ROUND(RAND() * 500, 2), ROUND(RAND() * 10000, 2),
             FLOOR(RAND() * 1000000000 + 100000000), 'Transfer Transaction', 'Completed', ROUND(RAND() * 5, 2));
        """),
        ("Delete Cancelled Transactions", """
        DELETE FROM BankTransactions
        WHERE TransactionStatus = 'Cancelled';
        """),
        ("Update Transaction Type", """
        UPDATE BankTransactions
        SET TransactionType = 'UpdatedType'
        WHERE TransactionID = FLOOR(RAND() * 1000) + 1;
        """),
        ("Select Transaction Count", """
        SELECT COUNT(*) FROM BankTransactions;
        """)
    ],
    "olap": [
        ("Monthly Summary", """
        SELECT DATE_FORMAT(TransactionDate, '%Y-%m') AS Month, SUM(Amount) AS TotalTransactionAmount
        FROM BankTransactions
        GROUP BY Month;
        """),
        ("Account Summary", """
        SELECT AccountID, COUNT(*) AS TransactionCount, SUM(Amount) AS TotalAmount
        FROM BankTransactions
        GROUP BY AccountID;
        """),
        ("Transaction Status Summary", """
        SELECT TransactionStatus, COUNT(*) AS TotalTransactions
        FROM BankTransactions
        GROUP BY TransactionStatus;
        """),
        ("Daily Summary", """
        SELECT DATE(TransactionDate) AS Day, SUM(Amount) AS DailyTotal
        FROM BankTransactions
        GROUP BY Day;
        """),
        ("Max Transaction Amount", """
        SELECT MAX(Amount) AS MaxTransactionAmount FROM BankTransactions;
        """),
        ("Avg Balance", """
        SELECT AVG(BalanceAfterTransaction) AS AvgBalance FROM BankTransactions;
        """),
        ("Amount Range Summary", """
        SELECT CASE 
                   WHEN Amount < 100 THEN 'Low'
                   WHEN Amount BETWEEN 100 AND 1000 THEN 'Medium'
                   ELSE 'High'
               END AS AmountRange, COUNT(*) AS Transactions
        FROM BankTransactions
        GROUP BY AmountRange;
        """),
        ("Top 5 Descriptions", """
        SELECT Description, COUNT(*) AS Total
        FROM BankTransactions
        GROUP BY Description
        ORDER BY Total DESC
        LIMIT 5;
        """)
    ]
}

# 執行 SQL 查詢並記錄效能數據
def execute_queries_with_metrics(oltp_ratio=70, loop_count=800):
    clear_performance_table()
    for i in range(loop_count):
        print(f"\n--- Executing Queries - Loop {i+1}/{loop_count} ---")
        query_type = "oltp" if random.randint(1, 100) <= oltp_ratio else "olap"
        query_name, query = random.choice(queries[query_type])

        try:
            queue_time = round(random.uniform(0.1, 0.3), 4)
            wait_time = round(random.uniform(0.05, 0.2), 4)
            time.sleep(queue_time)
            time.sleep(wait_time)

            start_time = time.time()
            cursor.execute(query)
            rows_scanned = cursor.rowcount
            end_time = time.time()

            execution_time = round(end_time - start_time, 4)
            throughput = round(rows_scanned / execution_time, 4) if execution_time > 0 else 0

            cursor.execute("""
                INSERT INTO OLTPOLAPPerformance 
                (QueryName, QueryType, QueueTime, WaitTime, ExecutionTime, RowsScanned, Throughput)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (query_name, query_type.upper(), queue_time, wait_time, execution_time, rows_scanned, throughput))
            connection.commit()

            print(f"{query_name} | Queue: {queue_time}s | Wait: {wait_time}s | Exec: {execution_time}s | Rows: {rows_scanned} | Throughput: {throughput}")

        except Exception as e:
            print(f"Error executing {query_name}: {e}")

# 主程式執行
try:
    execute_queries_with_metrics(oltp_ratio=50, loop_count=800)
except Exception as e:
    print(f"Error: {e}")
finally:
    cursor.close()
    connection.close()
    print("Database connection closed.")
