from flask import Flask
from database import init_db
from controllers import todo, category, courses_at_year, rating, courses, coordinators

init_db()

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

app.register_blueprint(todo.bp)
app.register_blueprint(category.bp)
app.register_blueprint(courses_at_year.bp)
app.register_blueprint(rating.bp)
app.register_blueprint(courses.bp)
app.register_blueprint(coordinators.bp)
