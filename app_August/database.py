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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS USERS (
            KU_ID CHAR(6),
            username CHAR(40),
            PRIMARY KEY (KU_ID)
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS COURSES (
            KURSUS_ID CHAR(10),
            coursename VARCHAR(70),
            description VARCHAR(2000),
            PRIMARY KEY (KURSUS_ID)
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS COURSE_COORDINATOR (
            CC_ID SERIAL PRIMARY KEY,
            name VARCHAR(40)
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS COURSE_AT_YEAR (
            KURSUS_ID CHAR(10),
            term VARCHAR(6),
            blok CHAR(1),
            PRIMARY KEY (KURSUS_ID, term),
            FOREIGN KEY (KURSUS_ID) REFERENCES COURSES(KURSUS_ID)
                ON UPDATE CASCADE
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS RATING (
            KU_ID CHAR(6),
            KURSUS_ID CHAR(10),
            term VARCHAR(6),
            time_stamp DATE,
            score INTEGER,
            comment VARCHAR(250),
            PRIMARY KEY (KU_ID, KURSUS_ID, term),
            FOREIGN KEY (KU_ID) REFERENCES USERS(KU_ID)
                ON UPDATE CASCADE
                ON DELETE SET NULL,
            FOREIGN KEY (KURSUS_ID, term) REFERENCES COURSE_AT_YEAR(KURSUS_ID, term)
                ON UPDATE CASCADE
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS COORDINATES (
            KURSUS_ID CHAR(10),
            term VARCHAR(6),
            CC_ID INTEGER,
            PRIMARY KEY (KURSUS_ID, term, CC_ID),
            FOREIGN KEY (KURSUS_ID, term) REFERENCES COURSE_AT_YEAR(KURSUS_ID, term)
                ON UPDATE CASCADE,
            FOREIGN KEY (CC_ID) REFERENCES COURSE_COORDINATOR(CC_ID)
        );
    """)
    
    
    conn.commit()

    df = pd.read_csv(os.path.join('data', 'combined.csv'))
    df2 = pd.read_csv(os.path.join('data', 'unique_courses.csv'))
    for _, row in df2.iterrows():
        cur.execute(
            '''
            INSERT INTO COURSES (KURSUS_ID, coursename, description)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            ''',
            (row['code_kuc'], row['title_kuh'], row['content'])
        )
    for _, row in df.iterrows():
        cur.execute(
            '''
            INSERT INTO COURSE_AT_YEAR (KURSUS_ID, term, blok)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            ''',
            (row['code_kuc'], row['term'], row['schedule'])
        )

    categories = ['DIS', 'House chores']
    for category in categories:
        cur.execute('INSERT INTO categories (category_name) VALUES (%s) ON CONFLICT DO NOTHING', (category,))

    todos = [('Assignment 1', 'DIS'), ('Groceries', 'House chores'), ('Assignment 2', 'DIS'), ('Project', 'DIS')]
    for (todo, category) in todos:
        cur.execute('INSERT INTO todos (todo_text, category_id) VALUES (%s, (SELECT id FROM categories WHERE category_name = %s)) ON CONFLICT DO NOTHING', (todo, category))

    conn.commit()
    conn.close()
