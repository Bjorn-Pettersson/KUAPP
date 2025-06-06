from flask import Blueprint, render_template, request
from models.courses import *
from models.rating import insert_rating

bp = Blueprint('courses', __name__, url_prefix='/')

@bp.route('/courses', methods=['GET', 'POST'])
def courses():
    sort = request.args.get('sort')
    desc = request.args.get('desc', '1') == '1'
    search_term = request.args.get('q', '').strip()
    if sort == 'rating':
        courses = list_courses(sort_by_rating=True, descending=desc, search_term=(search_term if search_term else None))
    else:
        courses = list_courses(search_term=(search_term if search_term else None))

    return render_template('courses.html', courses=courses)

@bp.route('/courses/<course_id>', methods=['GET', 'POST'])
def course_detail(course_id):
    term = request.args.get('term')
    if term=="all":
        term = None
    course, ratings = get_course_by_id(course_id, term)
    terms, latest_term = fetch_all_terms(course_id)
    error = None
    
    if request.method == 'POST':
        if 'comment' in request.form:
            comment_text = request.form['comment']
            kursus_id = request.form['kursus_id']
            score = int(request.form['score'])
            ku_id = request.form['KU_ID']  # Replace with actual user/session logic
            term = request.form['term']
            
            error = insert_rating(ku_id, kursus_id, term, score, comment_text)
            
    if not course:
        return render_template('404.html'), 404
    if not term or term=="all":
        return render_template('course_detail.html', course=course, ratings=ratings, error=error, terms=terms, latest_term=latest_term)
    return render_template('course_detail.html', course=course, ratings=ratings, error=error, terms=terms, selected_term=term,latest_term=latest_term) 
        