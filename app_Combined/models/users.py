from database import db_connection
from datetime import datetime
import re

class User:
    def __init__(self, ku_id, name):
        self.ku_id = ku_id
        self.name = name

def insert_user(ku_id, name):
    if not re.match(r'^[a-zA-Z]{3}[0-9]{3}$', ku_id):
            error = "Invalid KU ID. Must be 3 letters followed by 3 digits (e.g., zts900)."
            return 1
    else:
        conn = db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO USERS (KU_ID, username) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (ku_id, name)
        )
        conn.commit()
        conn.close()
        return 0