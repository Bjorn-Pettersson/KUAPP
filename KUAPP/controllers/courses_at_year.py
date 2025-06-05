from flask import Blueprint, render_template, request
from models.courses_at_year import CourseAtYear, list_courses_at_year
from models.rating import insert_rating

bp = Blueprint('courses_at_year', __name__, url_prefix='/')

@bp.route('/courses_at_year', methods=['GET', 'POST'])
def courses():
    search_term = request.args.get('q', '').strip()
    courses = list_courses_at_year(search_term=(search_term if search_term else None))

    return render_template('courses_at_year.html', courses=courses)
