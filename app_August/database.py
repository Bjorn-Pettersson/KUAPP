import psycopg2
import os
import pandas as pd

# Try to get from system enviroment variable
# Set your Postgres user and password as second arguments of these two next function calls
user = os.environ.get('PGUSER', 'postgres')
password = os.environ.get('PGPASSWORD', 'minkonto1')
host = os.environ.get('HOST', '127.0.0.1')

def db_connection():
    db = "dbname='todo' user=" + user + " host=" + host + " password =" + password
    conn = psycopg2.connect(db)

    return conn

def init_db():
    conn = db_connection()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS categories (id SERIAL PRIMARY KEY, category_name TEXT NOT NULL UNIQUE)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS todos (id SERIAL PRIMARY KEY, todo_text TEXT NOT NULL UNIQUE, category_id INTEGER NOT NULL, FOREIGN KEY(category_id) REFERENCES categories(id))''')
    cur.execute('''CREATE TABLE IF NOT EXISTS COURSE_AT_YEAR (course_ID VARCHAR(10) NOT NULL, course_name VARCHAR(100), term VARCHAR(6), PRIMARY KEY (course_ID, term))''')
    conn.commit()

    df = pd.read_csv(os.path.join('data', 'combined.csv'))
    for _, row in df.iterrows():
        cur.execute(
            '''
            INSERT INTO COURSE_AT_YEAR (course_ID, course_name, term)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            ''',
            (row['code_kuh'], row['title_kuh'], row['term'])
        )

    categories = ['DIS', 'House chores']
    for category in categories:
        cur.execute('INSERT INTO categories (category_name) VALUES (%s) ON CONFLICT DO NOTHING', (category,))

    todos = [('Assignment 1', 'DIS'), ('Groceries', 'House chores'), ('Assignment 2', 'DIS'), ('Project', 'DIS')]
    for (todo, category) in todos:
        cur.execute('INSERT INTO todos (todo_text, category_id) VALUES (%s, (SELECT id FROM categories WHERE category_name = %s)) ON CONFLICT DO NOTHING', (todo, category))

    conn.commit()
    conn.close()
