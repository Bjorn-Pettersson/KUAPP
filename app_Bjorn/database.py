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

    # ── 1. Drop old tables in dependency-safe order ────────────────────────────
    cur.execute("""
        DROP TABLE IF EXISTS rating          CASCADE;
        DROP TABLE IF EXISTS coordinates     CASCADE;
        DROP TABLE IF EXISTS course_overview  CASCADE;
        DROP TABLE IF EXISTS course_coordinator CASCADE;
        DROP TABLE IF EXISTS users           CASCADE;
        DROP TABLE IF EXISTS courses         CASCADE;
    """)
    conn.commit()

    # ── 2. Re-create tables ----------------------------------------------------

    # 2.1  courses  (master list, keyed by KU-id)
    cur.execute("""
        CREATE TABLE courses (
            code TEXT PRIMARY KEY,          -- e.g. NDAK15006U
            name TEXT NOT NULL,
            description TEXT,

            -- columns from ku_courses_reduced_2.csv
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
            code_kuc TEXT
        );
    """)

    # 2.2  users  (KU-ids that match 3 letters + 3 digits)
    cur.execute("""
        CREATE TABLE users (
            ku_id TEXT PRIMARY KEY,
            full_name TEXT,
            CONSTRAINT ku_id_format CHECK (ku_id ~ '^[A-Za-z]{3}[0-9]{3}$')
        );
    """)

    # 2.3  rating  (many-to-many between users and courses)
    cur.execute("""
        CREATE TABLE rating (
            course_code TEXT REFERENCES courses(code) ON DELETE CASCADE,
            ku_id       TEXT REFERENCES users(ku_id)  ON DELETE CASCADE,
            score       SMALLINT CHECK (score BETWEEN 1 AND 5),
            comment     TEXT,
            created_at  TIMESTAMPTZ DEFAULT NOW(),
            PRIMARY KEY (course_code, ku_id)
        );
    """)

    # 2.4  course_overview  (year-specific aggregates)
    cur.execute("""
        CREATE TABLE course_overview (
            id SERIAL PRIMARY KEY,
            course_code TEXT REFERENCES courses(code) ON DELETE CASCADE,
            year        INTEGER,
            avg_grade   NUMERIC
        );
    """)

    # 2.5  course_coordinator  + coordinates (many-to-many)
    cur.execute("""
        CREATE TABLE course_coordinator (
            id SERIAL PRIMARY KEY,
            name TEXT
        );
        CREATE TABLE coordinates (
            course_code    TEXT REFERENCES courses(code)            ON DELETE CASCADE,
            coordinator_id INTEGER REFERENCES course_coordinator(id) ON DELETE CASCADE,
            PRIMARY KEY (course_code, coordinator_id)
        );
    """)
    conn.commit()

    # ── 3. Load courses from CSV  ──────────────────────────────────────────────
    df = pd.read_csv("data/ku_courses_reduced_2.csv")   # adjust path if needed
    df = df.where(pd.notnull(df), None)                 # NaN → None

    for _, row in df.iterrows():
        cur.execute(
            f"""
            INSERT INTO courses ({', '.join(df.columns)})
            VALUES ({', '.join(['%s'] * len(df.columns))})
            ON CONFLICT (code) DO NOTHING;
            """,
            tuple(row[col] for col in df.columns)
        )

    conn.commit()
    conn.close()
    print(f"Inserted {len(df)} rows into courses table.")


if __name__ == "__main__":
    init_db()
