from database import db_connection
from models.category import Category

class Course:
    def __init__(self, id, name, description, avg_rating):
        self.id = id
        self.name = name
        self.description = description
        self.avg_rating = avg_rating

def list_courses():
    conn = db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT c.KURSUS_ID, c.coursename, c.description, AVG(r.score)
        FROM COURSES c
        LEFT JOIN RATING r ON c.KURSUS_ID = r.KURSUS_ID
        GROUP BY c.KURSUS_ID
    ''')
    db_Courses = cur.fetchall()
    Courses = []
    for db_Course in db_Courses:
        Courses.append(Course(
            db_Course[0], db_Course[1], db_Course[2], db_Course[3]
        ))
    conn.close()
    return Courses