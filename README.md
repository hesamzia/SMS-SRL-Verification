# SMS-Verification                                 # Continued                                      

## TODO
- [X] add DB path to config.py sample
- [X] do more while normalizing, specially against SQLInjection. remove all non alpha numerical.
- [X] some health check url
- [X] there is problem with JJ1000000 and JJ100
- [X] create requirements.txt (pip freeze)
- [ ] the insert will fail if there is a ' or " in excel file
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
- [ ] Trim too long SMS
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
This is a project for training python, Flask, Git and github, Codeium.
This project is one of MR. jadi mirmirani’s course named “sms verify with db and answer”.


