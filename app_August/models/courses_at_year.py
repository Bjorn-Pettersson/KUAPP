from database import db_connection
from models.category import Category

class CourseAtYear:
    def __init__(self, id, term, blok, name):
        self.id = id
        self.blok = blok
        self.term = term
        self.name = name

def list_courses_at_year():
    conn = db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT c.KURSUS_ID, c.term, c.blok, co.coursename
        FROM COURSE_AT_YEAR c
        JOIN COURSES co ON c.KURSUS_ID = co.KURSUS_ID
    ''')
    db_CoursesAtYear = cur.fetchall()
    CoursesAtYear = []
    for db_CourseAtYear in db_CoursesAtYear:
        CoursesAtYear.append(CourseAtYear(
            db_CourseAtYear[0], db_CourseAtYear[1], db_CourseAtYear[2], db_CourseAtYear[3]
        ))
    conn.close()
    return CoursesAtYear

def get_course_name(kursus_id):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT coursename FROM COURSES WHERE KURSUS_ID = %s", (kursus_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else ""