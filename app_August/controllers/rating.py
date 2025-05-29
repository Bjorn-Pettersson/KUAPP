from flask import Blueprint, render_template, request
from models.courses_at_year import CourseAtYear, list_courses_at_year
from models.rating import list_ratings

bp = Blueprint('ratings', __name__, url_prefix='/')

@bp.route('/ratings', methods=['GET', 'POST'])
def ratings():
    categories = list_ratings()
    return render_template('ratings.html', categories=categories)
