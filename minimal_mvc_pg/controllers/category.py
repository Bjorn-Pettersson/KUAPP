from flask import Blueprint, render_template, request
from models.todo import Todo, list_todos, insert_todo
from models.category import insert_category, list_categories

bp = Blueprint('category', __name__, url_prefix='/')

@bp.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'POST':
        category_name = request.form['category_name']
        insert_category(category_name)

    categories = list_categories()

    return render_template('category.html', categories=categories)
