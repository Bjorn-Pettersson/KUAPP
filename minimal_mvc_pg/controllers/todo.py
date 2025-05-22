from flask import Blueprint, render_template, request
from models.todo import list_todos, insert_todo
from models.category import list_categories

bp = Blueprint('todo', __name__, url_prefix='/')

@bp.route('/todo', methods=['GET', 'POST'])
def todos():
    if request.method == 'POST':
        todo_text = request.form['new_todo']
        category_id = request.form['category_todo']
        insert_todo(todo_text, category_id)

    categories = list_categories()

    todos = list_todos()

    return render_template('todo.html', todos=todos, categories=categories)
