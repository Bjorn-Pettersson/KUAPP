import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/university_courses")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
