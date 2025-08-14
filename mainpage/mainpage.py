import requests
import os

from flask import Blueprint, render_template, jsonify, request, jsonify, flash, redirect
from flask_login import login_required, current_user
from flask_cors import CORS

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from flask import current_app
from flask import has_request_context
if has_request_context():
    from flask import request
    from werkzeug.utils import secure_filename
else:
    from werkzeug.utils import secure_filename

from ..config import DATABASE_PATH, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, CALL_BACK_TOKEN
from ..models import InvalidSerial, Serial
from ..__main__ import app
from .mainfunc import import_database_from_excel, normalize_string

'''
 This is the main (mainpage) blueprint for the application.
 It handles the main page and profile page.
 '''
main = Blueprint('main', __name__)

CORS(main, resources={rf"/v1/{CALL_BACK_TOKEN}/process": {"origins": "*"}})


@main.route('/')
def index():
    print('/')
    return render_template('index.html')


@main.route('/profile')
@login_required        # Protect the profile page so only logged in users can access it. 
                       #Ensure the user is logged in to access the profile page
def profile():
    return render_template('profile.html', name=current_user.name)


@main.route('/healthok')
@login_required        # Protect the profile page so only logged in users can access it. 
                       #Ensure the user is logged in to access the profile page
def health_check():
    #This function is used to check if the server is running
    return jsonify({'response': 'ok'}) , 200


@main.route('/importdb', methods=['GET', 'POST'])
@login_required        # Protect the profile page so only logged in users can access it. 
                       #Ensure the user is logged in to access the profile page
def importdb():
    # This function is used call import_database_from_excel function for gets a excel file of lookup data
    # and failuers and imports that to my database. User who is logged in can access this function.
   # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # set the upload folder in the app config
    serials,failuers = 0,0  # initialize the number of imported serials and failuers to 0
    if request.method == 'POST': # if the request method is POST, it means that the user has uploaded a file
        if ('file' not in request.files):
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        #if user does not select a file, browser also submits an empty part without filename
        # so we check if the file is empty
        if (file.filename == ''):
            flash('No selected file')
            return redirect(request.url)
        # check if the file is allowed to be uploaded
        if (file and allowed_file(file.filename)):
            filename = secure_filename(file.filename)
            file_path = app.root_path + os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)  # save the file to the upload folder
            serials,failuers = import_database_from_excel(file_path)
            os.remove(file_path)  # remove the file after importing the data

    return render_template('importok.html', no_of_serials=serials, no_of_failuers=failuers)


def allowed_file(filename):
    """
    Check if the file is allowed to be uploaded based on its extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# v1 because in the future maybe i want to use another versions in the same time together
@main.route(f"/v1/{CALL_BACK_TOKEN}/process", methods = ['POST']) 
# Add CALL_BACK_TOKEN key to the address so that only the sender can contact this key, not the hackers. 
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
#    print('Received data:', data)
    if data :
        phone = data['phone']
        message = data['message']
#        print(f'Received message: "{message}" from {phone}')
#        answer = check_serial(message)
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
    print(f'Checking serial: {serial}')
    # Create an engine and a configured "Session" class
    engine = create_engine(f"sqlite:///{app.root_path}{DATABASE_PATH}")

    # Create a configured "Session" class
    Session = sessionmaker(bind=engine)   
    Base = declarative_base() 
    
    class InvalidSerial(Base):
        __tablename__ = 'invalids'
        invalid_serial = Column(Integer, primary_key=True)

    # Create the table
    Base.metadata.create_all(engine)

    # Create a session
    session = Session() 
 
    # Create a query
    query = session.query(InvalidSerial).filter(InvalidSerial.invalid_serial == serial)

    # Execute the query
    result = query.all()

    if len(result) == 1:
        return f"your serial number is invalid!({serial})"  # TODO: return the string provided by the customer

    class Serial(Base):
        __tablename__ = 'serials'
        id = Column(Integer, primary_key=True)
        ref = Column(String(50))
        desc = Column(String(100))
        start_serial = Column(String(50))
        end_serial = Column(String(50))
        date = Column(String(50))

    # Create the table
    Base.metadata.create_all(engine)

    # Create a session
    session = Session() 
 
    # Create a query
    query = session.query(Serial).filter(Serial.start_serial <= serial).filter(Serial.end_serial >= serial)

    # Execute the query
    result = query.all()

    if len(result) == 1:
        return f"I found your serial number!({serial})"    # TODO: return the string provided by the customer
    return f"I didn't find your serial number!({serial})"   # TODO: return the string provided by the customer


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
