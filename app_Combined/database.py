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
            description TEXT,
            latest_year INTEGER,
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
            term TEXT,
            coursename VARCHAR(70) NOT NULL,
            description TEXT,
            faculty_kuh TEXT,
            institute TEXT,
            ects_kuh TEXT,
            url_kuh TEXT,
            exam TEXT,
            re_exam TEXT,
            code_kuh TEXT,
            url_kuc TEXT,
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
            course_code TEXT,
            ects_kuc TEXT,
            level TEXT,
            duration TEXT,
            placement TEXT,
            blok CHAR(1),
            capacity TEXT,
            study_board TEXT,
            department TEXT,
            faculty_kuc TEXT,
            course_coordinator_name VARCHAR(40),
            last_modified TEXT,
            KURSUS_ID CHAR(10) NOT NULL,
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
            INSERT INTO COURSES (KURSUS_ID, coursename, description, latest_year)
            VALUES (%s, %s, %s, NULL)
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
        # schedule is blok, title_kuc is coursename, code_kuc is KURSUS_ID
        # content is description
    columns = [
        'term', 'coursename', 'description', 'faculty_kuh', 'institute',
        'ects_kuh', 'url_kuh', 'exam', 're_exam', 'code_kuh', 'url_kuc', 'volume',
        'education', 'content', 'learning_outcome', 'literature', 'recommended_prereq',
        'teaching_methods', 'workload', 'feedback_form', 'signup', 'exam_html', 'language',
        'course_code', 'ects_kuc', 'level', 'duration', 'placement', 'blok', 'capacity',
        'study_board', 'department', 'faculty_kuc', 'course_coordinator_name', 'last_modified',
        'KURSUS_ID', 'year'   # <-- Add 'year' here
    ]
    for _, row in df.iterrows():
        values = (
            row['term'],
            row['title_kuh'],
            row['content'],
            row['faculty_kuh'],
            row['institute'],
            row['ects_kuh'],
            row['url_kuh'],
            row['exam'],
            row['re_exam'],
            row['code_kuh'],
            row['url_kuc'],
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
            row['course_code'],
            row['ects_kuc'],
            row['level'],
            row['duration'],
            row['placement'],
            row['schedule'],
            row['capacity'],
            row['study_board'],
            row['department'],
            row['faculty_kuc'],
            row['course_coordinator_name'],
            row['last_modified'],
            row['code_kuc'],
            2000+int(row['term'][1:3])  #
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
            (row['code_kuc'],row['term'], row['course_coordinator_name'])
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
