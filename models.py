from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    sel_focus = db.Column(db.String(100), nullable=False)
    lesson_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_favorite = db.Column(db.Boolean, default=False)
    academic_standard = db.Column(db.String(200))
    sel_standard = db.Column(db.String(100))

class CopilotTip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.String(20))
    subject = db.Column(db.String(50))
    topic = db.Column(db.String(200))
    sel_focus = db.Column(db.String(100))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)