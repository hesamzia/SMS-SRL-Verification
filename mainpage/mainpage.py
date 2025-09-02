import os
import shutil
import datetime
from datetime import date

from flask import Blueprint, render_template, jsonify, request, jsonify, flash, redirect,url_for
from flask_login import login_required, current_user
from flask_cors import CORS

from sqlalchemy import func

from flask import current_app
from flask import has_request_context
if has_request_context():
    from flask import request
    from werkzeug.utils import secure_filename
else:
    from werkzeug.utils import secure_filename

from fileinput import filename

from ..config import UPLOAD_FOLDER, CALL_BACK_TOKEN

from ..models import User, Process_serials, Smslogs, open_session

from ..__main__ import app
from .mainfunc import import_database_from_excel, normalize_string, convertToBinaryData, write_file, save_message_to_db,send_sms, check_serial, allowed_file

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
    if not current_user.is_authenticated:
        return render_template('index.html', user_name= "Guest", data = None, all_count = None)

    # Create a session
    session = open_session()

    # Create a query 1
    query = session.query(Process_serials).filter(func.date(Process_serials.process_date) >= (date.today() - datetime.timedelta(days=30))).filter(func.date(Process_serials.process_date) <= date.today())


    # Execute the query 1
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


    # Create a query 2
    query = session.query(Process_serials.response, func.count(Process_serials.response)).group_by(Process_serials.response).filter(func.date(Process_serials.process_date) >= (date.today() - datetime.timedelta(days=30))).filter(func.date(Process_serials.process_date) <= date.today())

    # Execute the query 2
    response_counts = query.all()
    all_count={}
    if len(response_counts) > 0:
        for response, count in response_counts: 
            all_count[response] = count


    # create andExecute the query 3
    response_counts = session.query(Smslogs).filter(Smslogs.task == "import_database_from_excel").order_by(Smslogs.taskdate.desc()).limit(1).all()

    if len(response_counts) > 0:
        for serial_row in response_counts:
            last_import_date= datetime.datetime.strptime(serial_row.taskdate, '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S')
    else:   
        last_import_date = "No data"

    return render_template('index.html', user_name=current_user.name if current_user.is_authenticated else "Guest", data = {'smss': smss if len(smss) > 0 else None}, all_count = all_count if len(all_count) > 0 else None, last_import_date = last_import_date, permission_level = current_user.permission_level)


@main.route('/users')
def users():
    # Create a session
    session = open_session() 

    # Create a query
    try:
        query = session.query(User)

        all_users = query.all() 
    except Exception as e:
        flash(f'An error occurred in fetching users: {e}', 'danger')
    users = []
    if len(all_users) > 0:
        for user in all_users :
            id, email , name, job, permission_level, confirmed = user.id, user.email, user.name, user.job, user.permission_level, user.confirmed
            users.append({
                'id': id,
                'email': email,
                'name': name,
                'job': job,
                'permission_level': permission_level,
                'confirmed': confirmed})


    return render_template('users.html',user_name=current_user.name if current_user.is_authenticated else "Guest", data = {'users': users if len(users) > 0 else None}, permission_level = current_user.permission_level)


@main.route('/users', methods=['POST'])
def users_post():
    # This will save the changes made by the Administrator
    data = request.get_json()
    rec_id = data.get("id")
    role = data.get("role1")
    active = data.get("active1")


    # Create a session
    session = open_session()
    try:
        # Create a query
        session.query(User).filter_by(id=rec_id).update({'permission_level' : role, 'confirmed' : active})
    except Exception as e:
        flash('Error in updating user : {e}', 'danger')
        
    
    session.commit()
    session.close()

    return jsonify({"status": "success", "record": data})    



@main.route('/profile')
@login_required        # Protect the profile page so only logged in users can access it. 
                       #Ensure the user is logged in to access the profile page
def profile():
    if current_user.picture != None:
        write_file(current_user.picture, rf"{app.root_path}\static\assets\img\user_photo.jpg")
    else:
        shutil.copyfile(rf"{app.root_path}\static\assets\img\60111.jpg", rf"{app.root_path}\static\assets\img\user_photo.jpg")
                                    
    return render_template('profile.html', user=current_user)


@main.route('/profile', methods = ['POST'])
def profile_post():
    '''
    # This function is used to update the user profile
    # Create a session
    '''
    session = open_session() 

    f = request.files['imagefile']
    if f.filename == '':
        f.filename = rf"{app.root_path}\static\assets\img\user_photo.jpg"
    else :
        f.save(f.filename)
    
    empPicture = convertToBinaryData(f.filename)
    # update the user
    try:
        session.query(User).filter_by(email=current_user.email).update({'phone' : request.form.get('phone'),\
                'job' : request.form.get('job'),'birthday' : request.form.get('birthday'),\
                'gender' : request.form.get('gender'), 'language' : request.form.get('language'),\
                'address' : request.form.get('address'), 'picture' : empPicture})
    except Exception as e:
        flash('Error in updating user : {e}', 'danger')
        
    
    session.commit()
    session.close()

    return redirect(url_for('main.index', user_name = current_user.name))


@main.route('/test')
def test():
    return render_template('test.html', records=records)


@main.route('/test', methods = ['POST'])
def test_post():
    data = request.get_json()
    rec_id = data.get("id")
    name = data.get("name")
    email = data.get("email")

    # Update in "database"
    for rec in records:
        if rec["id"] == rec_id:
            rec["name"] = name
            rec["email"] = email
            break

    return jsonify({"status": "success", "record": data})


@main.route('/healthok')
@login_required        # Protect the profile page so only logged in users can access it. 
                       #Ensure the user is logged in to access the profile page
def health_check():
    '''
    This function is used to check if the server is running
    '''
    return jsonify({'response': 'ok'}) , 200


@main.route('/importdb', methods=['GET', 'POST'])
@login_required        # Protect the profile page so only logged in users can access it. 
                       #Ensure the user is logged in to access the profile page
def importdb():
    '''
     This function is used call import_database_from_excel function for gets a excel file of lookup data
     and failuers and imports that to my database. User who is logged in can access this function.
     app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # set the upload folder in the app config
    '''
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
    data = request.get_json()
    if data :
        phone = data['phone']
        message = data['message']
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



