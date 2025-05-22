import psycopg2
import os
import pandas as pd

# Environment variable fallbacks
user = os.environ.get('PGUSER', 'postgres')
password = os.environ.get('PGPASSWORD', 'lenses')
host = os.environ.get('HOST', '127.0.0.1')
dbname = 'kuappdb'

def db_connection():
    conn_str = f"dbname='{dbname}' user={user} host={host} password={password}"
    return psycopg2.connect(conn_str)

def init_db():
    conn = db_connection()
    cur = conn.cursor()

    # Create table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id SERIAL PRIMARY KEY,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL
        )
    ''')
    conn.commit()

    # Check if table is empty
    cur.execute('SELECT COUNT(*) FROM courses')
    row_count = cur.fetchone()[0]

    if row_count == 0:
        print("Courses table is empty. Loading data from CSV...")
        df = pd.read_csv('data/ku_courses_reduced.csv')  # adjust path if needed

        for _, row in df.iterrows():
            cur.execute('''
                INSERT INTO courses (code, name)
                VALUES (%s, %s)
                ON CONFLICT (code) DO NOTHING
            ''', (row['code'], row['name']))

        conn.commit()
        print(f"Inserted {len(df)} rows.")
    else:
        print("Courses table already contains data. Skipping insert.")

    conn.close()
