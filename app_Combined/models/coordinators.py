from database import db_connection

class CourseCoordinator:
    def __init__(self, name, avg_rating):
        self.name = name
        self.avg_rating = avg_rating

def list_coordinators(sort_by_rating=False, descending=True):
    conn = db_connection()
    cur = conn.cursor()
    order_clause = ""
    if sort_by_rating:
        order_clause = f"ORDER BY avg_rating {'DESC NULLS LAST' if descending else 'ASC NULLS LAST'}"
    cur.execute(f'''
        SELECT co.name, AVG(r.score) as avg_rating
        FROM COORDINATES co
        LEFT JOIN RATING r ON co.KURSUS_ID = r.KURSUS_ID and r.term = co.term
        GROUP BY co.name
        {order_clause}
    ''')
    db_Coordinators = cur.fetchall()
    Coordinators = []
    for db_Coordinator in db_Coordinators:
        Coordinators.append(CourseCoordinator(
            db_Coordinator[0], db_Coordinator[1]
        ))
    conn.close()
    return Coordinators