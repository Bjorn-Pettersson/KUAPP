from flask import Flask
from database import init_db
from controllers import courses_at_year, rating, courses, coordinators
from flask import Blueprint, render_template, request

init_db()

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("index.html")

app.register_blueprint(courses_at_year.bp)
app.register_blueprint(rating.bp)
app.register_blueprint(courses.bp)
app.register_blueprint(coordinators.bp)
