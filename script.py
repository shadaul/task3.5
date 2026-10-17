import psycopg2
import ast

db_link = 'postgresql://postgres:DilnazDaulet01@db.huzoymvxnkrzrfdpjnoa.supabase.co:5432/postgres'

conn = psycopg2.connect(db_link)

with open('task1_d.json', 'r', encoding='utf-8') as f:
    raw_data = f.read()

import re
clean_str = re.sub(r':([a-zA-Z_]+)\s*=>', r'"\1":', raw_data)

data = ast.literal_eval(clean_str)

cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS books;")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id NUMERIC PRIMARY KEY,
        title TEXT,
        author TEXT,
        genre TEXT,
        publisher TEXT,
        year INTEGER,
        price VARCHAR(20)
    )
""")

conn.commit()

insert_query = """
    INSERT INTO books (id, title, author, genre, publisher, year, price)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id) DO NOTHING;
"""
books_tuples = [
    (row['id'], row['title'], row['author'], row['genre'], row['publisher'], row['year'], row['price'])
    for row in data
]

cursor.executemany(insert_query, books_tuples)

cursor.execute("SELECT COUNT(*) FROM books;")
count = cursor.fetchone()[0]

conn.commit()
print(f"Total raws in db in table books: {count}")

cursor.execute("""
    CREATE TABLE summary_books AS 
    SELECT
        year AS publication_year, 
        COUNT (*) AS book_count, 
        
    ROUND(AVG(
        CASE
            WHEN price LIKE '€%' THEN REPLACE(price, '€', '')::NUMERIC * 1.2
            ELSE REPLACE(price, '$', '')::NUMERIC
        END
    ), 2) AS average_price
    FROM books
    GROUP BY year
""")

conn.commit()
print("succesfull")