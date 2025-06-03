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

    # Drop all tables in the correct order to avoid foreign key issues
    cur.execute("DROP TABLE IF EXISTS COORDINATES CASCADE;")
    cur.execute("DROP TABLE IF EXISTS RATING CASCADE;")
    cur.execute("DROP TABLE IF EXISTS COURSE_AT_YEAR CASCADE;")
    cur.execute("DROP TABLE IF EXISTS COURSE_COORDINATOR CASCADE;")
    cur.execute("DROP TABLE IF EXISTS COURSES CASCADE;")
    cur.execute("DROP TABLE IF EXISTS USERS CASCADE;")
    cur.execute("DROP TABLE IF EXISTS todos CASCADE;")
    cur.execute("DROP TABLE IF EXISTS categories CASCADE;")
    
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
            name VARCHAR(40),
            PRIMARY KEY (name)
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
            name VARCHAR(40),
            PRIMARY KEY (KURSUS_ID, term, name),
            FOREIGN KEY (KURSUS_ID, term) REFERENCES COURSE_AT_YEAR(KURSUS_ID, term)
                ON UPDATE CASCADE,
            FOREIGN KEY (name) REFERENCES COURSE_COORDINATOR(name)
        );
    """)
    
    
    conn.commit()

    df = pd.read_csv(os.path.join('data', 'coordinator_split.csv'))
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
            INSERT INTO COURSE_COORDINATOR (name)
            VALUES (%s)
            ON CONFLICT DO NOTHING
            ''',
            (row['course_coordinator_name'],)
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
    for _, row in df.iterrows():
        cur.execute(
            '''
            INSERT INTO COORDINATES (KURSUS_ID, term, name)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            ''',
            (row['code_kuc'],row['term'], row['course_coordinator_name'])
        )

    conn.commit()
    conn.close()
