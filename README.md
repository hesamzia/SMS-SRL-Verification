# Serial No. Verification                                                                
This is a project for training python, Flask, Git and github, Codeium, chatGPT.
This project was an example of a Python course on the internet Which I have customized and modified with my own needs and experiences.
In this example, I have tried to test some technologies and methods and turn it into a training example with the comments I have embedded in the program.

# Project Overview  
This is an application that verifies the authenticity of serial numbers of goods via SMS and web. This document is prepared to show the complete project plan, architecture diagram, database design, folder structure, technology stack, deployment guidelines, and feature roadmap for the serial number verification system.

# What Will We Learn & Test?
Python
Flask 
blueprint
flask_login
use SQLAlchemy to connect sqlite
mainmenu and authentication (my github https://github.com/hesamzia/Mainmenu_And_Authentication.git)
Html and bootstrap
save picture in database for profile
editable table for users (make a javascript for bootstrap html)

# System Architecture
Serial number inquiry is done through two ways: web (main application) and SMS. To access the SMS section and reply to SMS, you must subscribe through one of the SMS providers and this requires payment. Therefore, to reduce costs and allow proper testing during programming, a cached application has been prepared to simulate the operation of sending and receiving SMS, in which text messages are sent and received from port 5001 of the local host to port 5000 of the same local host through a web page. Both of these applications are present in this project.
![main page not logged in](img/Architecture.raw?raw=true)

# Technology Stack & Dependencies
Backend: Flask 3.1+
Database: sqlite3
ORM: SQLAlchemy
Frontend: HTML5 + Bootstrap 5  
requirments.txt 

# Flask Project Folder Structure
SMS-VERIFICATION/
|   config.py

|   models.py

|   __init__.py

|   __main__.py

|     
+---auth/              # authentication and menu
|     auth.py
|      __init__.py
|     
+---mainpage/          # Dashboard
|      mainfunc.py
|      mainpage.py
|     __init__.py
+---templates/         # Bootstrap HTMLs
       404.html
       500.html
       confirm_user.html
       forgot_password.html
       index.html
       login.html
       profile.html
       signup.html
       test.html
       users.html

# Database Structure
CREATE TABLE user (
        id INTEGER PRIMARY KEY, 
        email TEXT, password TEXT, 
        name TEXT, 
        phone text, 
        Address text, 
        job text, 
        birthday date, 
        gender varchar(1), 
        language varchar(20), 
        picture blob, 
        permission_level varchar(1), 
        confirmed varchar(1));

CREATE TABLE serials (
        id INTEGER NOT NULL,
        ref VARCHAR(50),
        "desc" VARCHAR(100),
        start_serial VARCHAR(50),
        end_serial VARCHAR(50),
        date VARCHAR(50),
        PRIMARY KEY (id)
);

CREATE TABLE invalids (
        invalid_serial VARCHAR(50) NOT NULL,
        PRIMARY KEY (invalid_serial)
);

CREATE TABLE process_serials(
        id integer PRIMARY KEY, 
        sender varchar(20), 
        message varchar(100), 
        serial varchar(30), 
        response varchar(1), 
        platform varchar(1), 
        process_date datetime);

CREATE TABLE smslogs (
        id INTEGER PRIMARY KEY, 
        task varchar(30), 
        taskdate datetime);

# Deployment Guide


# User Guide



## TODO
- [X] add DB path to config.py sample
- [X] do more while normalizing, specially against SQLInjection. remove all non alpha numerical.
- [X] some health check url
- [X] there is problem with JJ1000000 and JJ100
- [X] create requirements.txt (pip freeze)
- [X] the insert will fail if there is a ' or " in excel file-->I am safe because using sqlalchemy in correct way
- [X] another 10% problem :D
- [X] refactor name str in normalize function
- [X] change to use sqlalchemy in import database
- [X] Change the database is accessed with using sqlalchemy, except in the login section
- [X] in normalize, convert for example AB001 to AB000001 (max len ? say 15)
- [X] Add upload Excel file before importing
- [X] rate limit and stop the brute force
- [X] add call back token on sender site (a key on route that just sender know)
- [X] change html pages to a new admin bootstrap pages.
- [X] Add import and others to new bootstrap pages.
- [X] Arrange the page and menus according to future needs
- [X] log messages (sms and main menu search) in the database
- [X] Add report of number of messages, confirmed serials, failures and not found serials into the cards in top of page
- [X] Online Monitoring of last serials checked (show logged messages)
- [X] dismissible alerts
- [X] Check on serial from main page
- [X] Add 404 page
- [X] Add last import date
- [ ] Add licenses and authors
- [X] Fix SMS list and counts for last month
- [X] Add pie chart
- [X] Remove the extra files from bootstrap and ...
- [X] Add profie page
- [X] Add picture to profile and db
- [X] Confirming the signed-up user by the admin
- [X] User Permissions (one Admin user and others...)
- [X] Admin can see Users list
- [X] Logged user don't need signup,forget password and login
- [X] Fix blank data error in profile
- [X] Add user page and edit role and confirm signed up user (except admin)
- [X] Make the program code more modular.
- [X] Add error handler - It will become more perfect with time. 
- [ ] Readme and user manual
- [X] Fix signup and forgot_password bugs
- [X] Fix pie chart bug in index.html file script
      
![main page not logged in](img/mainpage_1756834563.raw?raw=true)








