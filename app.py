
from flask import Flask, request,jsonify
from pandas import read_excel
import requests
from flask_cors import CORS
import os 
import config
import sqlite3

database_path = os.path.dirname(os.path.realpath(__file__)) + config.DATABASE_PATH
data_path = os.path.dirname(os.path.realpath(__file__)) + config.EXCEL_PATH
app = Flask(__name__)
'''
Cross-Origin Resource Sharing (CORS) is an HTTP-header based mechanism that allows a server to indicate
 any origins (domain, scheme, or port) other than its own from which a browser should permit loading
   resources.
'''
CORS(app, resources={r"/v1/process": {"origins": "*"}})



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
    print('Processing request...')
    print('Received request:', request.data)
    print('Is jason:', request.is_json)
    data = request.get_json()
    print('Received data:', data)
    if data :
        phone = data['phone']
        message = data['message']
        print(f'Received message: "{message}" from {phone}')
        send_sms(phone, message)
        return jsonify({'response': 'Message received!'})
    else:
        print('No message received!')
        return jsonify({'error': 'No message received!'}), 400

def send_sms(receptor, message):
    '''
    This function get a MSIDN and a messeage and a phone number and sends it to the SMS provider
    in our instance we are send sms to http://localhost:5000
    if used SMS providr, we usually get a API and API key that we can use it to send sms.
    '''
    url = f'http://localhost:5001/receivesms'
    message = 'Hi ' + message + ' jan!...'
    data = {'message' : message, 'receptor' : receptor}
    response = requests.post(url, json = data)
    print(f'The message "{message}" was sent and the status code is {response.status_code}')
    return response

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
    '''
#   import_database_from_excel(data_path)

# TO do : make sure that data imported correctly, we need to backup the old data
# TO do : do some normalization
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
            ("{row["Reference Number"]}", "{row["Description"]}", "{row["Start Serial"]}", 
            "{row["End Serial"]}", "{row["Date"]}");"""
        cur.execute(query)
    # TO do some more error handling
        serial_counter += 1
        if serial_counter % 10 == 0:
            connection.commit()
            print(f'Imported {serial_counter} records to serials')

    connection.commit()

    df = read_excel(data_path, 1)     # this sheet contains failuers. only one column is needed
    faild_counter = 0
    for index, row in df.iterrows():
        query = f"""INSERT INTO invalids (invalid_serial) VALUES 
            ("{row["Faulty"]}");"""
        cur.execute(query)
    # TO do some more error handling
        faild_counter += 1
        if faild_counter % 10 == 0:
            connection.commit()
            print(f'Imported {faild_counter} records toserials')
    connection.commit()
    connection.close()

    return


def check_serial():
    pass

if __name__ == "__main__":
   import_database_from_excel()
   #app.run("localhost", 5000, debug=True)
#txt = main_page()

#print(txt)


   
