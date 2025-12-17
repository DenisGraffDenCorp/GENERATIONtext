import sys
import os
import sqlite3
import random
import time

SYMBOLS = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя .,!?')


def get_next_symbol(context, cursor, order):
    """Выбор следующего символа из БД на основе контекста"""
    cursor.execute('''
        SELECT symbol, probability FROM transitions
        WHERE order_num = ? AND context = ?
    ''', (order, context))
    
    rows = cursor.fetchall()
    if not rows:
        return None
    
    symbols = [row[0] for row in rows]
    probs = [row[1] for row in rows]
    
    total = sum(probs)
    if total == 0:
        return None
    probs = [p / total for p in probs]
    
    return random.choices(symbols, weights=probs, k=1)[0]


def generate_text(prefix, db_path, max_length=500, max_order=13):
    """Генерация текста на основе цепей Маркова"""
    prefix = prefix.strip().lower()
    
    valid_prefix = ''.join(ch for ch in prefix if ch in SYMBOLS)
    if valid_prefix != prefix:
        print(f"Предупреждение: недопустимые символы удалены")
        prefix = valid_prefix
    
    if not prefix:
        print("Ошибка: начало текста не может быть пустым после фильтрации")
        return prefix
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    order = min(len(prefix), max_order)
    
    current_text = prefix
    print(f"\nИспользуется порядок {order}\n")
    print(f"Сгенерированный текст:\n{current_text}", end='', flush=True)
    
    start_time = time.time()
    generated_count = 0
    
    for i in range(max_length - len(prefix)):
        found = False
        
        for try_order in range(order, -1, -1):
            if try_order > 0:
                context = current_text[-try_order:]
            else:
                context = ''
            
            next_sym = get_next_symbol(context, cursor, try_order)
            if next_sym is not None:
                current_text += next_sym
                print(next_sym, end='', flush=True)
                generated_count += 1
                found = True
                break
        
        if not found:
            break
    
    conn.close()
    
    elapsed = time.time() - start_time
    print(f"\n\nГенерация завершена. Сгенерировано {generated_count} символов за {elapsed:.2f} сек")
    return current_text


def main():
    if len(sys.argv) < 2:
        print(f"Использование: python {sys.argv[0]} <путь_к_бд> [макс_длина]")
        print(f"Пример: python {sys.argv[0]} markov.db 500")
        sys.exit(1)
    
    db_path = sys.argv[1]
    max_length = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    
    if not os.path.exists(db_path):
        print(f"Ошибка: файл БД {db_path} не найден")
        print(f"Сначала запустите: python SQLDB.py . markov.db")
        sys.exit(1)
    
    print("=" * 60)
    print("Генератор текстов на основе цепей Маркова")
    print("=" * 60)
    print(f"База данных: {db_path}")
    print(f"Максимальная длина: {max_length}")
    print("=" * 60 + "\n")
    
    while True:
        prefix = input("Введите начало текста (или 'выход' для выхода):\n> ")
        if prefix.lower() in ('выход', 'quit'):
            print("\nПрограмма завершена")
            break
        
        if not prefix.strip():
            print("Ошибка: начало текста не может быть пустым\n")
            continue
        
        generate_text(prefix, db_path, max_length)
        print()


if __name__ == "__main__":
    main()
