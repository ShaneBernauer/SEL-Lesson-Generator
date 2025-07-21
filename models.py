
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.String(20))
    subject = db.Column(db.String(50))
    topic = db.Column(db.String(100))
    sel_focus = db.Column(db.String(50))
    lesson_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
