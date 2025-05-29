import re
from flask import Flask, render_template, request, redirect, url_for
from database import db_connection, init_db
import psycopg2
from database import db_connection, init_db, update_course_overview 

app = Flask(__name__)
init_db()


@app.route('/course/<code>/<path:term>', methods=['GET', 'POST'])
def course_detail(code, term):
    conn = db_connection()
    cur = conn.cursor()
    error = None

    # Always fetch the course first
    cur.execute("SELECT * FROM courses WHERE code = %s AND term = %s", (code, term))
    course = cur.fetchone()
    course_columns = [desc[0] for desc in cur.description]
    course_dict = dict(zip(course_columns, course)) if course else None

    if not course_dict:
        conn.close()
        return "Course not found", 404

    if request.method == 'POST':
        ku_id = request.form.get('ku_id', '').strip()
        rating = request.form.get('rating')
        comment = request.form.get('comment')

        if not re.match(r'^[a-zA-Z]{3}[0-9]{3}$', ku_id):
            error = "Invalid KU ID. Must be 3 letters followed by 3 digits (e.g., zts900)."
        else:
            try:
                cur.execute("INSERT INTO users (ku_id) VALUES (%s) ON CONFLICT (ku_id) DO NOTHING", (ku_id,))
                cur.execute('''
                    INSERT INTO rating (course_code, course_term, ku_id, score, comment)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (code, term, ku_id, rating, comment))

                # Update average rating for this specific course instance
                cur.execute("SELECT AVG(score) FROM rating WHERE course_code = %s AND course_term = %s", (code, term))
                new_avg = cur.fetchone()[0]
                cur.execute("UPDATE courses SET avg_rating = %s WHERE code = %s AND term = %s", (new_avg, code, term))

                conn.commit()
                return redirect(url_for('course_detail', code=code, term=term))

            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                error = "You have already submitted a rating for this course."
            except Exception as e:
                conn.rollback()
                error = f"An unexpected error occurred: {str(e)}"

    # Fetch ratings for this specific course instance
    cur.execute("""
        SELECT r.ku_id, r.score, r.comment, r.created_at
        FROM rating r
        WHERE r.course_code = %s AND r.course_term = %s
        ORDER BY r.created_at DESC
    """, (code, term))
    ratings = cur.fetchall()

    # Compute average rating for display (even though it's in DB)
    cur.execute("SELECT AVG(score) FROM rating WHERE course_code = %s AND course_term = %s", (code, term))
    avg_rating_result = cur.fetchone()
    average_rating = round(avg_rating_result[0], 2) if avg_rating_result[0] is not None else None

    conn.close()

    return render_template(
        'course_detail.html',
        course=course_dict,
        ratings=ratings,
        error=error,
        average_rating=average_rating
    )

@app.route('/overview/<base_code>')
def course_overview(base_code):
    update_course_overview()  
    conn = db_connection()
    cur = conn.cursor()

    # Fetch all courses with the same course_code (across terms)
    cur.execute("""
        SELECT * FROM courses
        WHERE course_code = %s
        ORDER BY term DESC
    """, (base_code,))
    courses = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    course_list = [dict(zip(columns, row)) for row in courses]

    # Fetch average of averages (avg_avg_rating)
    cur.execute("""
        SELECT avg_avg_rating FROM course_overview
        WHERE course_code = %s
    """, (base_code,))
    avg_avg_rating = cur.fetchone()
    conn.close()

    return render_template("overview.html",
                           base_code=base_code,
                           course_list=course_list,
                           avg_avg_rating=avg_avg_rating[0] if avg_avg_rating else None)


@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    search_term = ''

    if request.method == 'POST':
        search_term = request.form.get('search', '')
        conn = db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT code, name, term FROM courses
            WHERE name ILIKE %s OR code ILIKE %s
            ORDER BY term DESC
        """, (f'%{search_term}%', f'%{search_term}%'))
        results = cur.fetchall()
        conn.close()

    return render_template('index.html', results=results, search_term=search_term)


if __name__ == '__main__':
    app.run(debug=True)
