import sys
import os
import sqlite3
import csv

def create_database(csv_dir, db_path='markov.db'):
    """Загружает все CSV файлы в SQLite базу данных"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transitions (
            order_num INTEGER,
            context TEXT,
            symbol TEXT,
            probability REAL,
            PRIMARY KEY (order_num, context, symbol)
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_context ON transitions(context)')
    
    total_rows = 0
    
    for order in range(0, 14):
        csv_path = os.path.join(csv_dir, f'order_{order}.csv')
        if not os.path.exists(csv_path):
            print(f"Файл {csv_path} не найден, пропускаю")
            continue
        
        print(f"Загружаю order_{order}.csv...", end=' ', flush=True)
        
        rows_count = 0
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute('''
                    INSERT INTO transitions (order_num, context, symbol, probability)
                    VALUES (?, ?, ?, ?)
                ''', (
                    int(row['order']),
                    row['context'],
                    row['symbol'],
                    float(row['probability'])
                ))
                rows_count += 1
        
        conn.commit()
        total_rows += rows_count
        print(f"{rows_count} строк")
    
    cursor.execute('VACUUM')
    conn.close()
    
    print(f"\nВсего загружено {total_rows} переходов в {db_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Использование: python {sys.argv[0]} <папка_с_csv> [путь_бд]")
        print(f"Пример: python {sys.argv[0]} . markov.db")
        sys.exit(1)
    
    csv_dir = sys.argv[1]
    db_path = sys.argv[2] if len(sys.argv) > 2 else 'markov.db'
    
    if not os.path.isdir(csv_dir):
        print(f"Ошибка: папка {csv_dir} не найдена")
        sys.exit(1)
    
    create_database(csv_dir, db_path)
