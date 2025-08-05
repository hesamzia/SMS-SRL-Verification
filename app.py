
from flask import Flask, request,jsonify
from pandas import read_excel
import requests
from flask_cors import CORS
import os 
import config
import sqlite3
import re


database_path = os.path.dirname(os.path.realpath(__file__)) + config.DATABASE_PATH
data_path = os.path.dirname(os.path.realpath(__file__)) + config.EXCEL_PATH
app = Flask(__name__)

'''
Cross-Origin Resource Sharing (CORS) is an HTTP-header based mechanism that allows a server to indicate
 any origins (domain, scheme, or port) other than its own from which a browser should permit loading
   resources.
'''
CORS(app, resources={r"/v1/process": {"origins": "*"}})


@app.route("/v1/healthok")
def health_check():
    #This function is used to check if the server is running
    return jsonify({'response': 'ok'}) , 200


@app.route("/")
def main_page():
    #This the main page of the site
    return "Hello, Flask!!"


# v1 because in the future maybe i want to use another versions in the same time together
@app.route('/v1/process', methods = ['POST'])
def process():
    '''
    This function is used to get messages from An intermediate server that receives SMS from the SMS provider
      and sends it through a tunnel to our computer on port 5000 of the localhost. Since it was difficult 
      for me to get an SMS provider license and a VPS, I send the messages directly from an HTML that 
      I created. 
    '''
#    print('Processing request...')
#    print('Received request:', request.data)
#    print('Is jason:', request.is_json)
    data = request.get_json()
 #   print('Received data:', data)
    if data :
        phone = data['phone']
        message = data['message']
        print(f'Received message: "{message}" from {phone}')
        answer = check_serial(normalize_string(message))
        send_sms(phone, answer)
        return jsonify({'response': 'Message received!'})
    else:
        print('No message received!')
        return jsonify({'error': 'No message received!'}), 400


def check_serial(serial):
    """
    This function get a serial number and checks if it is valid or not and returns appropriate answer
    , after cosulting with database
    """
    connection = sqlite3.connect(database_path)
    cur = connection.cursor()
    
    query = f"SELECT * FROM invalids WHERE invalid_serial = '{serial}'"
    print(query)
    result  = cur.execute(query)
    if len(result.fetchall()) == 1:
        return "your serial number is invalid!"  # TODO: return the string provided by the customer
    

    query = f"SELECT * FROM serials WHERE start_serial < '{serial}' and end_serial > '{serial}'"
    print(query)
    result  = cur.execute(query)
    if len(result.fetchall()) == 1:
        return "I found your serial number!"    # TODO: return the string provided by the customer
    connection.close()
    return "I didn't find your serial number!"   # TODO: return the string provided by the customer


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
            print(f'Imported {faild_counter} records toserials')
    connection.commit()
    connection.close()

    return (serial_counter, faild_counter)



if __name__ == "__main__":
    a,b =import_database_from_excel()
    print(f'imported {a} serials and {b} failuers')
    app.run("localhost", 5000, debug=True)
#txt = main_page()

#print(txt)


   
