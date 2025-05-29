from database import db_connection
from datetime import datetime
from models.users import insert_user

class Rating:
    def __init__(self, ku_id, kursus_id, term, time_stamp, score, comment):
        self.ku_id = ku_id
        self.kursus_id = kursus_id
        self.term = term
        self.time_stamp = time_stamp
        self.score = score
        self.comment = comment

def list_ratings():
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT KU_ID, KURSUS_ID, term, time_stamp, score, comment FROM RATING")
    db_ratings = cur.fetchall()
    ratings = []
    for row in db_ratings:
        ratings.append(Rating(*row))
    conn.close()
    return ratings

def insert_rating(ku_id, kursus_id, term, score, comment, time_stamp=None, user_name=None):
    # Ensure user exists (insert_user uses ON CONFLICT DO NOTHING)
    if user_name is None:
        user_name = "Unknown"  # fallback if no name provided
    insert_user(ku_id, user_name)

    conn = db_connection()
    cur = conn.cursor()
    if time_stamp is None:
        time_stamp = datetime.now()
    cur.execute(
        "INSERT INTO RATING (KU_ID, KURSUS_ID, term, score, comment, time_stamp) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
        (ku_id, kursus_id, term, score, comment, time_stamp)
    )
    conn.commit()
    conn.close()