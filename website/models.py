from . import db
from flask_login import UserMixin

user_job = db.Table(
    'user_job',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('job_id', db.Integer, db.ForeignKey('job.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(100))

    saved = db.relationship('Job', secondary='user_job', backref='saves')

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    company = db.Column(db.String(150))
    url = db.Column(db.String(1000), unique=True)
    location = db.Column(db.String(150))
    salary = db.Column(db.String(150))