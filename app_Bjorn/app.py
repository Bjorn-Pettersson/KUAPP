from flask import Flask, render_template, request
from database import db_connection, init_db

app = Flask(__name__)
init_db()  # Only runs at startup

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    search_term = ''

    if request.method == 'POST':
        search_term = request.form.get('search', '')
        conn = db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT code, name FROM courses
            WHERE name ILIKE %s OR code ILIKE %s
        """, (f'%{search_term}%', f'%{search_term}%'))
        results = cur.fetchall()
        conn.close()

    return render_template('index.html', results=results, search_term=search_term)

if __name__ == '__main__':
    app.run(debug=True)
