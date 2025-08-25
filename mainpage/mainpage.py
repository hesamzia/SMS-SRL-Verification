import requests
import os
import datetime
from datetime import date

from flask import Blueprint, render_template, jsonify, request, jsonify, flash, redirect,url_for
from flask_login import login_required, current_user
from flask_cors import CORS

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from flask import current_app
from flask import has_request_context
if has_request_context():
    from flask import request
    from werkzeug.utils import secure_filename
else:
    from werkzeug.utils import secure_filename

from fileinput import filename

from ..config import DATABASE_PATH, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, CALL_BACK_TOKEN
from ..models import InvalidSerial, Serial, User
from ..__main__ import app
from .mainfunc import import_database_from_excel, normalize_string

'''
 This is the main (mainpage) blueprint for the application.
 It handles the main page and profile page.
 '''
main = Blueprint('main', __name__)

CORS(main, resources={rf"/v1/{CALL_BACK_TOKEN}/process": {"origins": "*"}})


@app.errorhandler(404)
def page_not_found(e):
    # If the request context is available, log the error
    if has_request_context():
        print(f"Page not found: {e}")
    # Handle 404 errors (page not found)
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    # Handle 500 errors (internal server error)
    if has_request_context():
        print(f"Internal server error: {e}")
    return render_template('500.html'), 500


@main.route('/<user_name>', defaults={'username': "Guest"})
@main.route('/<user_name>')
@main.route('/')
def index(user_name="Guest"):
    print(f'user in root: {user_name}')
    if not current_user.is_authenticated:
        return render_template('index.html', user_name= "Guest", data = None, all_count = None)
        # Create an engine and a configured "Session" class
    engine = create_engine(f"sqlite:///{app.root_path}{DATABASE_PATH}")

    # Create a configured "Session" class
    Session = sessionmaker(bind=engine)   
    Base = declarative_base() 
    
    class Process_serials(Base):
        __tablename__ = 'process_serials'
        id = Column(Integer, primary_key=True)
        sender = Column(String(20))
        message = Column(String(100))
        serial = Column(String(30))
        response = Column(String(1))
        platform = Column(String(1))
        process_date = Column(String(50), default='')  # You can set a default value or use a function to get the current date

    class Smslogs(Base):
        __tablename__ = 'smslogs'
        extend_existing=True
        id = Column(Integer, primary_key=True)
        task = Column(String(30))
        taskdate = Column(String(50))


     # Create the table
    Base.metadata.create_all(engine)

    # Create a session
    session = Session() 

    # Create a query
    query = session.query(Process_serials).filter(func.date(Process_serials.process_date) >= (date.today() - datetime.timedelta(days=30))).filter(func.date(Process_serials.process_date) <= date.today())
    # Execute the query
    all_smss = query.all()
    smss = []
    if len(all_smss) > 0:
        for sms in all_smss :
            sender, message, serial, response, platform = sms.sender, sms.message, sms.serial, sms.response, sms.platform
            process_date = sms.process_date 
            smss.append({
                'sender': sender,
                'message': message,
                'serial': serial,
                'response': response,
                'platform': platform,
                'process_date': process_date
            })
    query = session.query(Process_serials.response, func.count(Process_serials.response)).group_by(Process_serials.response).filter(func.date(Process_serials.process_date) >= (date.today() - datetime.timedelta(days=30))).filter(func.date(Process_serials.process_date) <= date.today())
    response_counts = query.all()
    all_count={}
    if len(response_counts) > 0:
        for response, count in response_counts: 
            all_count[response] = count

    response_counts = session.query(Smslogs).filter(Smslogs.task == "import_database_from_excel").order_by(Smslogs.taskdate.desc()).limit(1).all()
    if len(response_counts) > 0:
        for serial_row in response_counts:
            last_import_date= datetime.datetime.strptime(serial_row.taskdate, '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S')
    else:   
        last_import_date = "No data"

#    response_counts = query.all()

    return render_template('index.html', user_name=current_user.name if current_user.is_authenticated else "Guest", data = {'smss': smss if len(smss) > 0 else None}, all_count = all_count if len(all_count) > 0 else None, last_import_date = last_import_date)


@main.route('/profile')
@login_required        # Protect the profile page so only logged in users can access it. 
                       #Ensure the user is logged in to access the profile page
def profile():
    write_file(current_user.picture, rf"{app.root_path}\static\assets\img\user_photo.jpg")
                                    
    print("User photo written to user_photo.jpg")
    return render_template('profile.html', user=current_user)


@main.route('/profile', methods = ['POST'])
def profile_post():
    # This function is used to update the user profile

    # Create an engine and a configured "Session" class
    engine = create_engine(f"sqlite:///{app.root_path}{DATABASE_PATH}")

    # Create a configured "Session" class
    Session = sessionmaker(bind=engine)   
    Base = declarative_base() 

    # Create the table
    Base.metadata.create_all(engine)

    # Create a session
    session = Session() 
    f = request.files['imagefile']
    if f.filename == '':
        f.filename = rf"{app.root_path}\static\assets\img\user_photo.jpg"
    else :
        f.save(f.filename)
    
    empPicture = convertToBinaryData(f.filename)
    # Create a query
    session.query(User).filter_by(email=current_user.email).update({'phone' : request.form.get('phone'),\
            'job' : request.form.get('job'),'birthday' : request.form.get('birthday'),\
            'gender' : request.form.get('gender'), 'language' : request.form.get('language'),\
            'address' : request.form.get('address'), 'picture' : empPicture})
        
    
    session.commit()
    session.close()

    return redirect(url_for('main.index', user_name = current_user.name))

@main.route('/test')
def test():
    return render_template('test.html')


@main.route('/test', methods = ['POST'])
def test_post():
    return render_template('test.html')


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
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        #if user does not select a file, browser also submits an empty part without filename
        # so we check if the file is empty
        if (file.filename == ''):
            flash('No selected file', 'danger')
            return redirect(request.url)
        # check if the file is allowed to be uploaded
        if (file and allowed_file(file.filename)):
            filename = secure_filename(file.filename)
            file_path = app.root_path + os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)  # save the file to the upload folder
            serials,failuers = import_database_from_excel(file_path)
            os.remove(file_path)  # remove the file after importing the data
            flash(f'Successfully imported {serials} serials and {failuers} failuers from the file.', 'success')
        else:
            flash('File type not allowed', 'danger')
    print(f'user in importdb: {current_user.name}')
    return redirect(url_for('main.index', user_name = current_user.name))
#render_template(url_for('main.index', user_name = current_user.name))


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
        save_message_to_db(phone, message, answer,'S')  # Save the message to the database
        return jsonify({'response': 'Message received!'})
    else:
        print('No message received!')
        return jsonify({'error': 'No message received!'}), 400


@main.route("/check_one_serial", methods = ['POST']) 
@login_required        # Protect the profile page so only logged in users can access it. 
                       #Ensure the user is logged in to access the profile page
def check_one_serial():
    """
    This function is used to check one serial number and return the result.
    It is used in the index.html file to check the serial number.
    """
    if request.method == 'POST':
        serial = request.form.get('serial')
        if serial:
            answer = check_serial(normalize_string(serial), sender = True)
            save_message_to_db(current_user.name, serial, answer,'A')  # Save the message to the database
            return redirect(url_for('main.index', user_name = current_user.name))
        else:
            flash('Please enter a serial number.', 'danger')
            return redirect(url_for('main.index', user_name = current_user.name))
    else:
        flash('Invalid request method.', 'danger')
        return redirect(url_for('main.index', user_name = current_user.name))


def check_serial(serial, sender = None):
    """
    This function get a serial number and checks if it is valid or not and returns appropriate answer
    , after cosulting with database
    """
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
        if sender is not None:
            flash(f"Your serial number is invalid! ({serial})", 'danger') # Flash message for the user in search
            return (f"your serial number is invalid! ({serial})")   # If the serial is invalid, return None
        else:
            return (f"your serial number is invalid! ({serial})")  # TODO: return the string provided by the customer

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


def save_message_to_db(phone, message, answer, platform):
    """
    This function saves the message to the database.
    It creates a new record in the database with the phone number, message, answer, and platform.
    """
    engine = create_engine(f"sqlite:///{app.root_path}{DATABASE_PATH}")
    Base = declarative_base()

    class Message(Base):
        __tablename__ = 'process_serials'
        id = Column(Integer, primary_key=True)
        sender = Column(String(20))
        message = Column(String(100))
        serial = Column(String(30))
        response = Column(String(1))
        platform = Column(String(1))
        process_date = Column(String(50), default='')  # You can set a default value or use a function to get the current date

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)

    session = Session()
    
    normalized_message = ''
    if "invalid" in answer: 
        response = 'I'
        normalized_message = normalize_string(message)
    elif "valid" in answer: 
        response = 'V'
        normalized_message = normalize_string(message)
    else: 
        response = 'N'  # N for not found


    new_message = Message(sender=phone, message=message, serial=normalized_message, response=response, platform=platform,
         process_date=datetime.datetime.now())
    session.add(new_message)
    session.commit()
    session.close()
    return 


def convertToBinaryData(filename):
    # Convert digital data to binary format
    print(f'Converting file {filename} to binary data...')
    if not filename or not os.path.isfile(filename):
        print(f'File {filename} does not exist.')
        return None
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData


def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    print(f'Writing binary data to file {filename}...')
    with open(filename, 'wb+') as file:
        print(f'Converting binary data to file {filename}...')
        file.write(data)
