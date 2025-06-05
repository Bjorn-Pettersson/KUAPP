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
            coursename VARCHAR(100),
            content TEXT,
            latest_year INTEGER,
            PRIMARY KEY (KURSUS_ID)
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS COURSE_COORDINATOR (
            name VARCHAR(100),
            PRIMARY KEY (name)
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS COURSE_AT_YEAR (
            url TEXT,
            coursename VARCHAR(100) NOT NULL,
            volume TEXT,
            education TEXT,
            content TEXT,
            learning_outcome TEXT,
            literature TEXT,
            recommended_prereq TEXT,
            teaching_methods TEXT,
            workload TEXT,
            feedback_form TEXT,
            signup TEXT,
            exam_html TEXT,
            language TEXT,
            KURSUS_ID CHAR(10) NOT NULL,
            ects TEXT,
            level TEXT,
            duration TEXT,
            placement TEXT,
            blok VARCHAR(30),
            capacity TEXT,
            study_board TEXT,
            department TEXT,
            faculty TEXT,
            course_coordinators TEXT,
            last_modified TEXT,
            term TEXT,
            course_coordinator_name VARCHAR(100),
            year INTEGER,
            PRIMARY KEY (KURSUS_ID, term),
            FOREIGN KEY (KURSUS_ID) REFERENCES COURSES(KURSUS_ID)
                ON UPDATE CASCADE
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS RATING (
            KU_ID CHAR(6),
            KURSUS_ID CHAR(10),
            term TEXT,
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
            term TEXT,
            name VARCHAR(100),
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
            INSERT INTO COURSES (KURSUS_ID, coursename, content, latest_year)
            VALUES (%s, %s, %s, NULL)
            ON CONFLICT DO NOTHING
            ''',
            (row['course_code'], row['title'], row['content'])
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
    columns = [
        'url', 'coursename', 'volume', 'education', 'content', 'learning_outcome', 'literature',
        'recommended_prereq', 'teaching_methods', 'workload', 'feedback_form', 'signup',
        'exam_html', 'language', 'KURSUS_ID', 'ects', 'level', 'duration', 'placement',
        'blok', 'capacity', 'study_board', 'department', 'faculty', 'course_coordinators',
        'last_modified', 'term', 'course_coordinator_name', 'year'
    ]

    for _, row in df.iterrows():
        values = (
            row['url'],
            row['title'],
            row['volume'],
            row['education'],
            row['content'],
            row['learning_outcome'],
            row['literature'],
            row['recommended_prereq'],
            row['teaching_methods'],
            row['workload'],
            row['feedback_form'],
            row['signup'],
            row['exam_html'],
            row['language'],
            row['course_code'],      # KURSUS_ID in table
            row['ects'],
            row['level'],
            row['duration'],
            row['placement'],
            row['schedule'],         # blok in table
            row['capacity'],
            row['study_board'],
            row['department'],
            row['faculty'],
            row['course_coordinators'],
            row['last_modified'],
            row['term'],
            row['course_coordinator_name'],
            2000 + int(row['term'][1:3])  # or your year logic
        )
        cur.execute(
            f"""
            INSERT INTO COURSE_AT_YEAR (
                {', '.join(columns)}
            )
            VALUES ({', '.join(['%s'] * len(columns))})
            ON CONFLICT (KURSUS_ID, term) DO NOTHING;
            """,
            values
        )
    for _, row in df.iterrows():
        cur.execute(
            '''
            INSERT INTO COORDINATES (KURSUS_ID, term, name)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            ''',
            (row['course_code'],row['term'], row['course_coordinator_name'])
        )

    conn.commit()
    cur.execute(
        '''
        UPDATE COURSES
        SET latest_year = sub.max_year
        FROM (
            SELECT KURSUS_ID, MAX(year) AS max_year
            FROM COURSE_AT_YEAR
            GROUP BY KURSUS_ID
        ) AS sub
        WHERE COURSES.KURSUS_ID = sub.KURSUS_ID;
        '''
    )
    conn.commit()
    conn.close()
