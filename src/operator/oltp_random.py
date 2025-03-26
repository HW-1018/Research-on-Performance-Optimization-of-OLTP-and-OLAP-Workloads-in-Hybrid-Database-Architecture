import pymysql
import time

# 連接到 SingleStore (MySQL-compatible database)
connection = pymysql.connect(
    host="127.0.0.1",        # Replace with your database host
    user="root",             # Replace with your username
    password="4601",     # Replace with your password
    database="BANK"          # Replace with your database name
)
cursor = connection.cursor()

# 定義 8 個 SQL 語句
queries = [
    # 1. 隨機插入一筆新交易紀錄
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
    # 2. 隨機更新特定交易的狀態
    """
    UPDATE BankTransactions
    SET TransactionStatus = CASE FLOOR(RAND() * 2)
                              WHEN 0 THEN 'Completed'
                              ELSE 'Failed'
                           END
    WHERE TransactionID = FLOOR(RAND() * 1000) + 1;
    """,
    # 3. 隨機刪除某筆交易紀錄
    """
    DELETE FROM BankTransactions
    WHERE TransactionID = FLOOR(RAND() * 1000) + 1;
    """,
    # 4. 查詢指定帳戶最近的交易紀錄
    """
    SELECT *
    FROM BankTransactions
    WHERE AccountID = FLOOR(RAND() * 1000000000 + 100000000)
    ORDER BY TransactionDate DESC
    LIMIT 5;
    """,
    # 5. 隨機更新交易手續費資訊
    """
    UPDATE BankTransactions
    SET Fee = ROUND(RAND() * 20, 2)
    WHERE TransactionType = 'Withdrawal' 
      AND TransactionDate >= DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 7 + 1) DAY);
    """,
    # 6. 隨機新增轉帳交易
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
    # 7. 查詢每個帳戶總交易金額和次數
    """
    SELECT 
        AccountID, 
        COUNT(*) AS TransactionCount, 
        SUM(Amount) AS TotalTransactionAmount
    FROM 
        BankTransactions
    WHERE 
        TransactionDate >= DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 30 + 1) DAY)
    GROUP BY 
        AccountID
    ORDER BY 
        TotalTransactionAmount DESC;
    """,
    # 8. 隨機刪除已取消交易
    """
    DELETE FROM BankTransactions
    WHERE TransactionStatus = 'Cancelled' 
    AND TransactionDate BETWEEN DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 10 + 1) DAY) 
                            AND NOW();
    """
]

# 執行每個 SQL 語句 100 次
def execute_queries():
    try:
        for loop in range(1, 801):
            print(f"--- Loop {loop}/800 ---")
            for idx, query in enumerate(queries, start=1):
                print(f"Executing Query {idx}...")
                cursor.execute(query)
                if query.strip().upper().startswith("SELECT"):
                    result = cursor.fetchall()
                    print(f"Query {idx}: Returned {len(result)} rows.")
                else:
                    connection.commit()
                    print(f"Query {idx}: Executed successfully.")
            time.sleep(0.01)  # 可選，延遲 0.5 秒避免壓力過大
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        cursor.close()
        connection.close()
        print("Database connection closed.")

# 主程式執行
execute_queries()