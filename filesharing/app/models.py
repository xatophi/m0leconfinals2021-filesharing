from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    files = db.relationship('File', backref='user', lazy=True)

class File(db.Model):
    uuid = db.Column(db.String(length=32), primary_key=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.Text, nullable=False)

class SharedFile(db.Model):
    file_uuid = db.Column(db.String(length=32), db.ForeignKey('file.uuid'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)