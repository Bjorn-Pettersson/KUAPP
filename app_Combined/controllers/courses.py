from flask import Blueprint, render_template, request
from models.courses import *
from models.rating import insert_rating

bp = Blueprint('courses', __name__, url_prefix='/')

@bp.route('/courses', methods=['GET', 'POST'])
def courses():
    sort = request.args.get('sort')
    desc = request.args.get('desc', '1') == '1'
    if sort == 'rating':
        courses = list_courses(sort_by_rating=True, descending=desc)
    else:
        courses = list_courses()

    return render_template('courses.html', courses=courses)

@bp.route('/courses/<course_id>')
def course_detail(course_id):
    course = get_course_by_id(course_id)  # You need to implement this function
    if not course:
        return render_template('404.html'), 404
    return render_template('course_detail.html', course=course)