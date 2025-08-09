import sqlite3    # TODO : change with sqlalchemy
from pandas import read_excel
import re
from ..__main__ import app
from ..config import EXCEL_PATH, DATABASE_PATH



def import_database_from_excel():

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
    '''
#   import_database_from_excel(data_path)

# TODO : make sure that data imported correctly, we need to backup the old data
# TODO : do some normalization
    # sqllit database contains two tables : serials and invalids
    database_path = f"{app.root_path}{DATABASE_PATH}"
    data_path = f"{app.root_path}{EXCEL_PATH}"

    connection = sqlite3.connect(database_path)
    cur = connection.cursor()
    # remove the serials table is exists then create a new one
    cur.execute("DROP TABLE IF EXISTS serials")
    # create new serials table
    cur.execute("""CREATE TABLE IF NOT EXISTS serials (
	    id INTEGER PRIMARY KEY,
   	    ref TEXT,
	    desc TEXT,
        start_serial TEXT,
        end_serial TEXT,
        date DATE
        );
                """)
    cur.execute("DROP TABLE IF EXISTS invalids")
     # create new serials table
    cur.execute("""CREATE TABLE IF NOT EXISTS invalids (
   	    invalid_serial TEXT PRIMARY KEY
        );
                """)
    connection.commit()

    df = read_excel(data_path, 0)     # This sheet contains lookup data
    serial_counter = 0
    for index, row in df.iterrows():
        query = f"""INSERT INTO serials (ref, desc, start_serial, end_serial, date) VALUES 
            ("{row["Reference Number"]}", "{row["Description"]}", "{normalize_string(row["Start Serial"])}", 
            "{normalize_string(row["End Serial"])}", "{row["Date"]}");"""
        cur.execute(query)
    # TODO some more error handling
        serial_counter += 1
        if serial_counter % 10 == 0:
            connection.commit()
            print(f'Imported {serial_counter} records to serials')

    connection.commit()

    df = read_excel(data_path, 1)     # this sheet contains failuers. only one column is needed
    faild_counter = 0
    for index, row in df.iterrows():
        query = f"""INSERT INTO invalids (invalid_serial) VALUES 
            ("{normalize_string(row["Faulty"])}");"""
        cur.execute(query)
    # TODO some more error handling
        faild_counter += 1
        if faild_counter % 10 == 0:
            connection.commit()
            print(f'Imported {faild_counter} records to serials')
    connection.commit()
    connection.close()

    return (serial_counter, faild_counter)


def normalize_string(data):
    '''
    This function get a string and normalizes it (changes prsian number to english one and uppers it and 
    remove non-numeric characters)
    '''
    data = data.upper()    # make string uppercase
    data = re.sub(r'\W', '', data)  # remove non-numeric characters
    from_char = '۰۱۲۳۴۵۶۷۸۹'
    to_char = '0123456789'
    data = data.translate(data.maketrans(from_char, to_char))    # change persian numbers to english
    return data  
    # TODO : add more normalization rules if needed