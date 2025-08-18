import re
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pandas import read_excel

from ..__main__ import app, db
from ..config import DATABASE_PATH


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
# TODO : make sure that data imported correctly, we need to backup the old data
# TODO : do more normalization
    # sqllit database contains two tables : serials and invalids

    # Create a SQLAlchemy engine
    engine = create_engine(f"sqlite:///{app.root_path}{DATABASE_PATH}")

    # Create a base class for declarative class definitions
    Base = declarative_base()

    # Create a metadata object
    metadata = MetaData()
    metadata.clear()             # clear the metadata object to avoid conflicts
    metadata.reflect(bind=engine)   # reflect the database schema into the metadata

    # Drop the table serials if it exists
    serials_table = Table('serials', metadata)
    serials_table.drop(engine, checkfirst=True)  # drop the table serials using checkfirst=True to avoid errors if 
                                                # the table doesn't exist
    invalids_table = Table('invalids', metadata)
    invalids_table.drop(engine, checkfirst=True)  # drop the table invalids using

    metadata.clear() # clear the metadata object again to avoid conflicts
    metadata.reflect(bind=engine)   # reflect the database schema into the metadata again for the new tables


    # Define the tables serials and invalids using SQLAlchemy

    table_name1 = 'serials'
    table_name2 = 'invalids'

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


    # Create the tables
    metadata.create_all(engine)

    # Create a session for the database, we will use to add data to the database 
    Session = sessionmaker(bind=engine)
    session = Session()    # create a session to interact with the database

 
    df = read_excel(file_path, 0)     # This sheet contains lookup data
    serial_counter = 0
    for index, row in df.iterrows():
        session.execute(my_table1.insert(), 
            [{'ref': row["Reference Number"], 
            'desc': row["Description"], 
            'start_serial': normalize_string(row["Start Serial"]), 
            'end_serial': normalize_string(row["End Serial"]), 
            'date': row["Date"]}])     # insert data into the serials table
    # TODO : some more error handling
        serial_counter += 1


    df = read_excel(file_path, 1)     # this sheet contains failuers. only one column is needed
    faild_counter = 0
    for index, row in df.iterrows():
        session.execute(my_table2.insert(), 
            [{'invalid_serial': normalize_string(row["Faulty"])}])   # insert data into the invalids table
    # TODO some more error handling
        faild_counter += 1

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
    # TODO : add more normalization rules if needed


