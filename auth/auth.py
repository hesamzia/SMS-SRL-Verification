from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from ..__main__ import db, app
from ..models import User
'''
 This is the auth blueprint for the application.
 It handles user authentication, including login, signup, and logout.
 '''
auth = Blueprint('auth', __name__)

# Initialize Flask-Limiter
#limiter = Limiter(app, key_func=get_remote_address)
limiter = Limiter(get_remote_address, 
        app=app, 
        default_limits=["1200 per day", "100 per hour"], 
        storage_uri="memory://")

@auth.route('/login')
@limiter.limit("5 per minute")  # Limit login attempts to 5 per minute
def login():
    # code to validate and login user goes here
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    print("before query")
    user = User.query.filter_by(email=email).first()
    print("after query")
    user_name = user.name if user else None  # Get the user's name if the user exists
    print(f"User Name: {user_name}")  # Debugging line to check the user's name

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.','danger')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    if user.confirmed != 'y':
        flash('Administrator has not confirmed your account yet.', 'danger')
        return redirect(url_for('auth.login'))

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.index', user_name = user_name)) # Redirect to the main page after successful login


@auth.route('/forgot_password')
def forgot_password():
    # This will render the forgot password page where users can request a password reset
    # This is a placeholder for the forgot password functionality
    return render_template('forgot_password.html')


@auth.route('/forgot_password', methods=['POST'])
@limiter.limit("5 per minute")  # Limit login attempts to 5 per minute
def forgot_password_post():
    # This will handle the logic for processing the forgot password request
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Email address not found. Please try again.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    return redirect(url_for('main.index',user_name = current_user.name)) # Redirect to the main page after successful login


@auth.route('/signup')
def signup():
    # code to validate and signup user goes here
    # This will render the signup page where users can create an account
     return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    
    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists', 'danger')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'))
    
    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required     # Protect the logout page so only logged in users can access it. 
                    #Ensure the user is logged in to access the profile page
def logout():
    # code to logout user goes here
    # This will handle user logout logic, such as clearing session data
    logout_user()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('main.index'))  # Redirect to the main page after logout
# Note: The user_name is set to default (Guest) after logout to indicate that no user is logged in.
# This can be adjusted based on your application's requirements.