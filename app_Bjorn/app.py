from flask import Flask, render_template, request
from database import db_connection, init_db

app = Flask(__name__)
init_db()  # Only runs at startup

@app.route('/course/<code>')
def course_detail(code):
    conn = db_connection()
    cur = conn.cursor()

    # Fetch the course by code
    cur.execute('''
        SELECT * FROM courses WHERE code = %s
    ''', (code,))
    course = cur.fetchone()

    # Get column names for rendering
    colnames = [desc[0] for desc in cur.description]

    conn.close()

    if course:
        course_dict = dict(zip(colnames, course))
        return render_template('course_detail.html', course=course_dict)
    else:
        return "Course not found", 404


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
