import re
from flask import Flask, render_template, request, redirect, url_for
from database import db_connection, init_db

app = Flask(__name__)
init_db()


@app.route('/course/<code>', methods=['GET', 'POST'])
def course_detail(code):
    conn = db_connection()
    cur = conn.cursor()
    error = None

    if request.method == 'POST':
        ku_id = request.form.get('ku_id', '').strip()
        rating = request.form.get('rating')
        comment = request.form.get('comment')

        # Validate KU ID
        if not re.match(r'^[a-zA-Z]{3}[0-9]{3}$', ku_id):
            error = "Invalid KU ID. Must be 3 letters followed by 3 digits (e.g., zts900)."
        else:
            # Ensure user exists
            cur.execute("INSERT INTO users (ku_id) VALUES (%s) ON CONFLICT (ku_id) DO NOTHING", (ku_id,))

            # Insert new rating
            cur.execute('''
                INSERT INTO rating (course_code, ku_id, score, comment)
                VALUES (%s, %s, %s, %s)
            ''', (code, ku_id, rating, comment))
            conn.commit()
            return redirect(url_for('course_detail', code=code))

    # Fetch course
    cur.execute("SELECT * FROM courses WHERE code = %s", (code,))
    course = cur.fetchone()
    course_columns = [desc[0] for desc in cur.description]
    course_dict = dict(zip(course_columns, course)) if course else None

    # Fetch all ratings for this course
    cur.execute("""
        SELECT r.ku_id, r.score, r.comment, r.created_at
        FROM rating r
        WHERE r.course_code = %s
        ORDER BY r.created_at DESC
    """, (code,))
    ratings = cur.fetchall()
    conn.close()

    if course_dict:
        return render_template('course_detail.html', course=course_dict, ratings=ratings, error=error)
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
