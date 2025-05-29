from database import db_connection
from datetime import datetime

class User:
    def __init__(self, ku_id, name):
        self.ku_id = ku_id
        self.name = name

def insert_user(ku_id, name):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO USERS (KU_ID, username) VALUES (%s, %s) ON CONFLICT DO NOTHING",
        (ku_id, name)
    )
    conn.commit()
    conn.close()