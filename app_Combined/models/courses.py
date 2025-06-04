from database import db_connection
from models.rating import Rating

class Course:
    def __init__(self, id, name, description, avg_rating):
        self.id = id
        self.name = name
        self.description = description
        self.avg_rating = avg_rating

class CourseFull:
    def __init__(self, id, name, description, blok, institut, ects, sprog, term, coordinator, avg_rating):
        self.id = id
        self.name = name
        self.description = description
        self.block = blok         # assign to .block
        self.institut = institut  # assign to .institut
        self.ects = ects          # assign to .ects
        self.sprog = sprog        # assign to .sprog
        self.term = term        # assign to .sprog
        self.coordinator = coordinator
        self.avg_rating = avg_rating

def list_courses(sort_by_rating=False, descending=True, search_term=None):
    conn = db_connection()
    cur = conn.cursor()
    order_clause = ""
    if sort_by_rating:
        order_clause = f"ORDER BY avg_rating {'DESC NULLS LAST' if descending else 'ASC NULLS LAST'}"
    if search_term:
        cur.execute(f'''
            SELECT c.KURSUS_ID, c.coursename, c.content, AVG(r.score) as avg_rating
            FROM COURSES c
            LEFT JOIN RATING r ON c.KURSUS_ID = r.KURSUS_ID
            WHERE c.coursename ILIKE %s OR c.KURSUS_ID ILIKE %s        
            GROUP BY c.KURSUS_ID, c.coursename, c.content
            {order_clause}
        ''', (f'%{search_term}%',f'%{search_term}%'))
    else:
        cur.execute(f'''
            SELECT c.KURSUS_ID, c.coursename, c.content, AVG(r.score) as avg_rating
            FROM COURSES c
            LEFT JOIN RATING r ON c.KURSUS_ID = r.KURSUS_ID
            GROUP BY c.KURSUS_ID, c.coursename, c.content
            {order_clause}
        ''')
    db_Courses = cur.fetchall()
    Courses = []
    for db_Course in db_Courses:
        Courses.append(Course(
            db_Course[0], db_Course[1], db_Course[2], db_Course[3]
        ))
    conn.close()
    return Courses

def get_course_by_id(course_id, term=None):
    conn = db_connection()
    cur = conn.cursor()
    if term==None:
        cur.execute('''
            SELECT c.KURSUS_ID, c.coursename, c.content,
                ca.blok, ca.department, ca.ects, ca.language, ca.term, ca.course_coordinator_name
            FROM (SELECT * FROM COURSES WHERE KURSUS_ID = %s) c
            JOIN COURSE_AT_YEAR ca
            ON c.KURSUS_ID = ca.KURSUS_ID AND ca.year = c.latest_year
            LIMIT 1
        ''', (course_id,))
        row = cur.fetchone()
        # Fetch ratings for this specific course instance
        cur.execute("""
            SELECT r.KU_ID, r.score, r.comment, r.time_stamp
            FROM rating r
            WHERE r.KURSUS_ID = %s
            ORDER BY r.time_stamp DESC
        """, (course_id,))
        ratings = cur.fetchall()
        conn.close()
    else:
        cur.execute('''
            SELECT c.KURSUS_ID, c.coursename, ca.content,
                ca.blok, ca.department, ca.ects, ca.language, ca.term, ca.course_coordinator_name
            FROM (SELECT * FROM COURSES WHERE KURSUS_ID = %s) c
            JOIN COURSE_AT_YEAR ca
            ON c.KURSUS_ID = ca.KURSUS_ID AND ca.term = %s
            LIMIT 1
        ''', (course_id,term,))
        row = cur.fetchone()
        # Fetch ratings for this specific course instance
        cur.execute("""
            SELECT r.KU_ID, r.score, r.comment, r.time_stamp
            FROM rating r
            WHERE r.KURSUS_ID = %s AND r.term = %s
            ORDER BY r.time_stamp DESC
        """, (course_id,term))
        ratings = cur.fetchall()
        conn.close()
    if row:
        return CourseFull(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], None), ratings
    return None, None

def fetch_all_terms(course_id):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT term, year FROM COURSE_AT_YEAR WHERE KURSUS_ID = %s ORDER BY year DESC, term DESC",
        (course_id,)
    )
    rows = cur.fetchall()
    terms = [row[0] for row in rows]
    latest_term = rows[0][0] if rows else None
    conn.close()
    return terms, latest_term