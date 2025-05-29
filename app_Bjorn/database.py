import psycopg2
import os
import pandas as pd

# ── connection parameters ──────────────────────────────────────────────────────
user     = os.environ.get('PGUSER',     'postgres')
password = os.environ.get('PGPASSWORD', 'lenses')
host     = os.environ.get('HOST',       '127.0.0.1')
dbname   = 'kuappdb'

def db_connection():
    conn_str = f"dbname='{dbname}' user={user} host={host} password={password}"
    return psycopg2.connect(conn_str)

# ── initialise / refresh the DB ────────────────────────────────────────────────
def init_db():
    conn = db_connection()
    cur  = conn.cursor()

    # 1. Drop the table if it already exists
    cur.execute('DROP TABLE IF EXISTS courses;')
    conn.commit()

    # 2. Re-create it with ALL required columns
    cur.execute('''
        CREATE TABLE courses (
            id SERIAL PRIMARY KEY,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,

            -- columns coming from ku_courses_reduced_2.csv
            title_kuh TEXT,
            faculty_kuh TEXT,
            institute TEXT,
            term TEXT,
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
            schedule TEXT,
            capacity TEXT,
            study_board TEXT,
            department TEXT,
            faculty_kuc TEXT,
            course_coordinators TEXT,
            last_modified TEXT,
            code_kuc TEXT,

            -- user-feedback fields (start out NULL)
            user_rating INTEGER,
            user_comment TEXT
        );
    ''')
    conn.commit()

    # 3. Load the CSV and insert its data  (feedback columns are left NULL)
    df = pd.read_csv('data/ku_courses_reduced_2.csv')   # adjust path if needed
    df = df.where(pd.notnull(df), None)                 # NaN → None

    for _, row in df.iterrows():
        cur.execute('''
            INSERT INTO courses (
                code, name, title_kuh, faculty_kuh, institute, term,
                ects_kuh, url_kuh, exam, re_exam, code_kuh, url_kuc, volume,
                education, content, learning_outcome, literature,
                recommended_prereq, teaching_methods, workload, feedback_form,
                signup, exam_html, language, course_code, ects_kuc, level,
                duration, placement, schedule, capacity, study_board,
                department, faculty_kuc, course_coordinators, last_modified,
                code_kuc
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s
            )
            ON CONFLICT (code) DO NOTHING;
        ''', tuple(row[col] for col in df.columns))

    conn.commit()
    conn.close()
    print(f"Inserted {len(df)} rows into extended courses table.")
