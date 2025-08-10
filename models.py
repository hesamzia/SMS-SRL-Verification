from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
'''
The user model represents what it means for the app to have a user. 
This tutorial will require fields for an email address, password, and name. 
In future applications, you may decide you want much more information to be stored per user. You can add things like birthdays, profile pictures, locations, or any user preferences.
'''
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


class Serial(UserMixin, db.Model):
    __tablename__ = 'serials'
    id = db.Column(db.Integer, primary_key=True)
    ref = db.Column(db.String(50))
    desc = db.Column(db.String(100))
    start_serial = db.Column(db.String(50))
    end_serial = db.Column(db.String(50))
    date = db.Column(db.String)

class InvalidSerial(UserMixin, db.Model):
    __tablename__ = 'invalids'
    invalid_serial = db.Column(db.String(50), primary_key=True)
