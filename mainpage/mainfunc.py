import requests
import re
import os
import datetime
from datetime import date

from flask import flash

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pandas import read_excel

from ..__main__ import app
from ..config import DATABASE_PATH, ALLOWED_EXTENSIONS, MAX_FLASHES
from ..models import open_session, Process_serials, InvalidSerial, Serial


def import_database_from_excel(file_path=None):

    '''
    gets a excel file of lookup data and failuers and imports that to my database.

    I will use sqllite to store the data. I need to remove the old data first and then import the new data
    we can add The path of database in config file

    df contains lookup data in the form of (sheet number 0):
    ROW	Reference Number	Description	Start Serial	End Serial	Date
    and second sheet contains failuers in the form of (sheet number 0):
    invalid serial
  
    This data is imported to my sqlite database that located in filepath database_path saved in config file
    and database file named database.sqlite
    excel file saved in filepath data_path saved in config file 
    
    returns the number of imported serials and failuers 
    After the import was complete, I decided to make a change to the application and used sqlalchemy.
    '''
    # sqllit database contains two tables : serials and invalids

    # Create a SQLAlchemy engine
    engine = create_engine(f"sqlite:///{app.root_path}{DATABASE_PATH}")

    # Create a base class for declarative class definitions
    Base = declarative_base()

    # Create a metadata object
    metadata = MetaData()
    metadata.clear()             # clear the metadata object to avoid conflicts
    metadata.reflect(bind=engine)   # reflect the database schema into the metadata

    try:
        # Drop the table serials if it exists
        serials_table = Table('serials', metadata)
        serials_table.drop(engine, checkfirst=True)  # drop the table serials using checkfirst=True to avoid errors if 
                                                    # the table doesn't exist
        invalids_table = Table('invalids', metadata)
        invalids_table.drop(engine, checkfirst=True)  # drop the table invalids using
    except:
        flash('Failed to drop tables in database', 'danger')

    metadata.clear() # clear the metadata object again to avoid conflicts
    metadata.reflect(bind=engine)   # reflect the database schema into the metadata again for the new tables


    # Define the tables serials and invalids using SQLAlchemy

    table_name1 = 'serials'
    table_name2 = 'invalids'
    table_name3 = 'smslogs'   # to log the import date
    try:
        my_table1 = Table(table_name1, metadata,
                    Column('id', Integer, primary_key=True),
                    Column('ref', String(50)), 
                    Column('desc', String(100)),
                    Column('start_serial', String(50)), 
                    Column('end_serial', String(50)), 
                    Column('date', String(50))
        )   
        
        my_table2 = Table(table_name2, metadata,
                    Column('invalid_serial', String(50), primary_key=True)
        )

    except:
        flash(f'Failed to create tables in database', 'danger')

    # Define the table smslogs
    class Smslogs(Base):
        __tablename__ = 'smslogs'
        extend_existing=True
        id = Column(Integer, primary_key=True)
        task = Column(String(30))
        taskdate = Column(String(50))


    # Create the tables
    metadata.create_all(engine)

    # Create a session for the database, we will use to add data to the database 
    Session = sessionmaker(bind=engine)
    session = Session()    # create a session to interact with the database

 
    df = read_excel(file_path, 0)     # This sheet contains lookup data
    serial_counter = 1
    total_flashes = 0
    for index, row in df.iterrows():
        try:
            session.execute(my_table1.insert(), 
                [{'ref': row["Reference Number"], 
                'desc': row["Description"], 
                'start_serial': normalize_string(row["Start Serial"]), 
                'end_serial': normalize_string(row["End Serial"]), 
                'date': row["Date"]}])     # insert data into the serials table
        except:    
            total_flashes += 1
            if total_flashes < MAX_FLASHES:
                flash(f'Failed to insert row {serial_counter} of excel file sheet serials into database', 'danger')
            else:
                flash('Too maney errors in excel file', 'danger')
                break

        serial_counter += 1
    session.commit()

    df = read_excel(file_path, 1)     # this sheet contains failuers. only one column is needed
    faild_counter = 1
    for index, row in df.iterrows():
        try:
            session.execute(my_table2.insert(), 
                [{'invalid_serial': normalize_string(row["Faulty"])}])   # insert data into the invalids table
        except:    
            total_flashes += 1
            if total_flashes < MAX_FLASHES:
                flash(f'Failed to insert row {faild_counter} of excel file sheet failuers into database', 'danger')
            else:
                flash('Too maney errors in excel file', 'danger')
                break
        faild_counter += 1
    session.commit()  # commit the changes to the database

 
    new_log = Smslogs(task="import_database_from_excel", taskdate=datetime.datetime.now())
    session.add(new_log)

    session.commit()  # commit the changes to the database
    session.close() # close the session Although by exiting the function the session will be closed automatically,
                    # it is a good practice to close the session explicitly

    return (serial_counter, faild_counter)


def normalize_string(data, max_numeric_lenght = 15): 
    # max_numeric_lenght is the maximum length of numeric part of the serial number
    '''
    This function get a string and normalizes it (changes prsian number to english one and uppers it and 
    remove non-numeric characters)
    '''
    data = str(data)  # make sure data is a string

    data = data.upper()    # make string uppercase
    data = re.sub(r'\W', '', data)  # remove non-numeric characters
    from_char = '۰۱۲۳۴۵۶۷۸۹'
    to_char = '0123456789'
    data = data.translate(data.maketrans(from_char, to_char))    # change persian numbers to english
    alpha_part = ''
    numeric_part = ''
    for char in data:
        if char.isalpha():
            alpha_part += char
        else:
            numeric_part += char
    # Add leading zeros to the numeric part
    numeric_length = max_numeric_lenght - len(alpha_part)
    numeric_part = numeric_part.zfill(numeric_length)

    # Combine the alphabetic and numeric parts
    data = alpha_part + numeric_part

    return data  


def convertToBinaryData(filename):
    # Convert digital data to binary format
    if not filename or not os.path.isfile(filename):
        flash(f'File {filename} does not exist.', 'danger')
        return None
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData


def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb+') as file:
        file.write(data)


def save_message_to_db(phone, message, answer, platform):
    '''
     This function saves the message to the database.
     It creates a new record in the database with the phone number, message, answer, and platform.
    '''
   
    session = open_session()  # Create a session
    
    normalized_message = ''
    if "invalid" in answer: 
        response = 'I'
        normalized_message = normalize_string(message)
    elif "valid" in answer: 
        response = 'V'
        normalized_message = normalize_string(message)
    else: 
        response = 'N'  # N for not found

    try:
        new_message = Process_serials(sender=phone, message=message, serial=normalized_message, response=response, platform=platform,
            process_date=datetime.datetime.now())
        session.add(new_message)
    except:
        flash(f'Failed to insert message into database', 'danger')
    session.commit()
    session.close()
    return 


def send_sms(receptor, message):
    '''
    This function get a MSIDN and a messeage and a phone number and sends it to the SMS provider
    in our instance we are send sms to http://localhost:5000
    if used SMS providr, we usually get a API and API key that we can use it to send sms.
    '''
    url = f'http://localhost:5001/receivesms'
    data = {'message' : message, 'receptor' : receptor}
    response = requests.post(url, json = data)
    print(f'The message "{message}" was sent and the status code is {response.status_code}')
    return response


def check_serial(serial, sender = None):
    """
    This function get a serial number and checks if it is valid or not and returns appropriate answer
    , after cosulting with database
    """

    # Create a session
    session = open_session()
 
    # Create a query
    query = session.query(InvalidSerial).filter(InvalidSerial.invalid_serial == serial)

    # Execute the query
    result = query.all()

    if len(result) == 1:
        if sender is not None:
            flash(f"Your serial number is invalid! ({serial})", 'danger') # Flash message for the user in search
            return (f"your serial number is invalid! ({serial})")   # If the serial is invalid, return None
        else:
            return (f"your serial number is invalid! ({serial})")  # TODO: return the string provided by the customer

    # Create a query
    query = session.query(Serial).filter(Serial.start_serial <= serial).filter(Serial.end_serial >= serial)

    # Execute the query
    result = query.all()

    if len(result) == 1:
        if sender is not None:
            flash(f"I found your serial number valid! ({serial})", 'success')
            return "valid"  # If the serial is valid, return None
        else:
            return f"I found your serial number valid!({serial})"    # TODO: return the string provided by the customer
    else:
        if sender is not None:
            flash(f"I didn't find your serial number! ({serial})", 'danger')
            return "not found"
        else:
            return f"I didn't find your serial number! ({serial})"   # TODO: return the string provided by the customer
    return None  # If no valid serial found, return None


def allowed_file(filename):
    """
    Check if the file is allowed to be uploaded based on its extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


