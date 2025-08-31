from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import current_app
from .config import DATABASE_PATH
#from . import database_path


db = SQLAlchemy()
'''
The user model represents what it means for the app to have a user. 
This tutorial will require fields for an email address, password, and name. 
In future applications, you may decide you want much more information to be stored per user. You can add things like birthdays, profile pictures, locations, or any user preferences.
'''
class User(UserMixin, db.Model):
    __tablename__ = 'user'
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
    picture = db.Column(db.LargeBinary)
    permission_level = db.Column(db.String(1)) 
    confirmed = db.Column(db.String(1))


class Serial(db.Model):
    __tablename__ = 'serials'
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    ref = db.Column(db.String(50))
    desc = db.Column(db.String(100))
    start_serial = db.Column(db.String(50))
    end_serial = db.Column(db.String(50))
    date = db.Column(db.String(50))

class InvalidSerial(db.Model):
    __tablename__ = 'invalids'
    invalid_serial = db.Column(db.String(50), primary_key=True) # primary keys are required by SQLAlchemy


class Process_serials(db.Model):
    __tablename__ = 'process_serials'
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(20))
    message = db.Column(db.String(100))
    serial = db.Column(db.String(30))
    response = db.Column(db.String(1))
    platform = db.Column(db.String(1))
    process_date = db.Column(db.String(50), default='')  # You can set a default value or use a function to get the current date

class Smslogs(db.Model):
    __tablename__ = 'smslogs'
    db.extend_existing=True
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(30))
    taskdate = db.Column(db.String(50))

def open_session() :
        # This will render the users page where Administrator can view and manage their account
    engine = create_engine(f"sqlite:///{current_app.root_path}{DATABASE_PATH}")

    # Create a configured "Session" class
    Session = sessionmaker(bind=engine)   
    Base = declarative_base() 
     # Create the table
    Base.metadata.create_all(engine)

    # Create a session
    session = Session() 

    return session

