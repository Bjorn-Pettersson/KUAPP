from database import db_connection

class Category:
    def __init__(self, id, name):
        self.id = id
        self.name = name

def list_categories():
    conn = db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, category_name FROM categories')
    db_categories = cur.fetchall()

    categories = []
    for db_category in db_categories:
        categories.append(Category(db_category[0], db_category[1]))
    conn.close()
    return categories

def insert_category(category_name):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO categories (category_name) VALUES (%s) ON CONFLICT DO NOTHING', (category_name,))
    conn.commit()
    cur.close()
    conn.close()
