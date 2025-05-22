from flask import Blueprint, render_template, request
from models.courses_at_year import CourseAtYear, list_courses_at_year

bp = Blueprint('courses', __name__, url_prefix='/')

@bp.route('/courses', methods=['GET', 'POST'])
def courses():
    courses = list_courses_at_year()

    return render_template('courses.html', courses=courses)
