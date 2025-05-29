from database import db_connection
from models.category import Category

class CourseAtYear:
    def __init__(self, id, term, blok):
        self.id = id
        self.blok = blok
        self.term = term

def list_courses_at_year():
    conn = db_connection()
    cur = conn.cursor()
    cur.execute('SELECT KURSUS_ID, term, blok FROM COURSE_AT_YEAR')
    db_CoursesAtYear = cur.fetchall()
    CoursesAtYear = []
    for db_CourseAtYear in db_CoursesAtYear:
        CoursesAtYear.append(CourseAtYear(db_CourseAtYear[0], db_CourseAtYear[1], db_CourseAtYear[2]))

    conn.close()
    return CoursesAtYear