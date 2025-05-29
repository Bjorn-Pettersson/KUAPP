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
