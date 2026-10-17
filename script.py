import psycopg2
from psycopg2.extras import execute_values
import ast
import re

db_link = 'postgresql://postgres:ochecnsloazhnui@db.huzoymvxnkrzrfdpjnoa.supabase.co:5432/postgres'

conn = psycopg2.connect(db_link)
cursor = conn.cursor()

with open('task1_d.json', 'r', encoding='utf-8') as f:
    raw_data = f.read()

clean_str = re.sub(r':([a-zA-Z_]+)\s*=>', r'"\1":', raw_data)
data = ast.literal_eval(clean_str)

cursor.execute("DROP TABLE IF EXISTS summary_books;")
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
    );
""")

conn.commit()

insert_query = """
    INSERT INTO books (id, title, author, genre, publisher, year, price)
    VALUES %s
    ON CONFLICT (id) DO NOTHING;
"""

books_tuples = [
    (row['id'], row['title'], row['author'], row['genre'], row['publisher'], row['year'], row['price'])
    for row in data
]

execute_values(cursor, insert_query, books_tuples)

cursor.execute("SELECT COUNT(*) FROM books;")
count = cursor.fetchone()[0]
print(f"Total rows in db in table books: {count}")

cursor.execute("""
    CREATE TABLE summary_books AS 
    SELECT
        year AS publication_year, 
        COUNT(*) AS book_count, 
        ROUND(AVG(
            CASE
                WHEN price LIKE '€%' THEN REPLACE(price, '€', '')::NUMERIC * 1.2
                ELSE REPLACE(price, '$', '')::NUMERIC
            END
        ), 2) AS average_price
    FROM books
    GROUP BY year;
""")

conn.commit()
print("Success! Summary table created.")

cursor.close()
conn.close()