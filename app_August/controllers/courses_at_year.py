from flask import Blueprint, render_template, request
from models.courses_at_year import CourseAtYear, list_courses_at_year

bp = Blueprint('courses_at_year', __name__, url_prefix='/')

@bp.route('/courses_at_year', methods=['GET', 'POST'])
def courses():
    courses = list_courses_at_year()

    return render_template('courses_at_year.html', courses=courses)
