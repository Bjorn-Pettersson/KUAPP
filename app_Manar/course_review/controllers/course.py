from flask import Blueprint, render_template, request, redirect, url_for

bp = Blueprint('course', __name__)

# Midlertidig "database"
reviews = []

@bp.route('/')
def index():
    return render_template('course.html', reviews=reviews)

@bp.route('/submit', methods=['POST'])
def submit():
    review = request.form.get('review')
    score = request.form.get('score')

    if review and score:
        reviews.append({'review': review, 'score': score})

    return redirect(url_for('course.index'))
