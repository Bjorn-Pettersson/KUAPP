from flask import Flask
from database import init_db
from controllers import course

init_db()

app = Flask(__name__)
app.register_blueprint(course.bp)

if __name__ == '__main__':
    app.run(debug=True)
