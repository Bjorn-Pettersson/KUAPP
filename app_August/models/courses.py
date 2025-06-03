from database import db_connection

class Course:
    def __init__(self, id, name, description, avg_rating):
        self.id = id
        self.name = name
        self.description = description
        self.avg_rating = avg_rating

def list_courses(sort_by_rating=False, descending=True):
    conn = db_connection()
    cur = conn.cursor()
    order_clause = ""
    if sort_by_rating:
        order_clause = f"ORDER BY avg_rating {'DESC NULLS LAST' if descending else 'ASC NULLS LAST'}"
    cur.execute(f'''
        SELECT c.KURSUS_ID, c.coursename, c.description, AVG(r.score) as avg_rating
        FROM COURSES c
        LEFT JOIN RATING r ON c.KURSUS_ID = r.KURSUS_ID
        GROUP BY c.KURSUS_ID, c.coursename, c.description
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