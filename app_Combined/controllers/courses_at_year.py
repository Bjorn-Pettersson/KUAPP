from flask import Blueprint, render_template, request
from models.courses_at_year import CourseAtYear, list_courses_at_year
from models.rating import insert_rating

bp = Blueprint('courses_at_year', __name__, url_prefix='/')

@bp.route('/courses_at_year', methods=['GET', 'POST'])
def courses():
    courses = list_courses_at_year()

    if request.method == 'POST':
        if 'comment' in request.form:
            comment_text = request.form['comment']
            kursus_id = request.form['kursus_id']
            score = int(request.form['score'])
            ku_id = request.form['KU_ID']  # Replace with actual user/session logic
            term = request.form['term']
            insert_rating(ku_id, kursus_id, term, score, comment_text)

    return render_template('courses_at_year.html', courses=courses)
