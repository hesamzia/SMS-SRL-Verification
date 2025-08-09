from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from .mainfunc import import_database_from_excel
'''
 This is the main (mainpage) blueprint for the application.
 It handles the main page and profile page.
 '''
main = Blueprint('main', __name__)

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


@main.route('/importdb')
@login_required        # Protect the profile page so only logged in users can access it. 
                       #Ensure the user is logged in to access the profile page
def importdb():
    # This function is used call import_database_from_excel function for gets a excel file of lookup data
    # and failuers and imports that to my database. User who is logged in can access this function.
    serials,failuers = import_database_from_excel()
    print(f'imported {serials} serials and {failuers} failuers')
    return render_template('importok.html', no_of_serials=serials, no_of_failuers=failuers)

