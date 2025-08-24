from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

#from . import database_path

# Create a SQLAlchemy engine  

#engine = create_engine(f"sqlite:///{app.root_path}{DATABASE_PATH}")
 

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
    phone = db.Column(db.String(100))
    job = db.Column(db.String(100))
    birthday = db.Column(db.String(50))
    gender = db.Column(db.String(1))
    language = db.Column(db.String(20))
    address = db.Column(db.String(100))


class Serial(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    ref = db.Column(db.String(50))
    desc = db.Column(db.String(100))
    start_serial = db.Column(db.String(50))
    end_serial = db.Column(db.String(50))
    date = db.Column(db.String(50))

class InvalidSerial(db.Model):
    invalid_serial = db.Column(db.String(50), primary_key=True) # primary keys are required by SQLAlchemy