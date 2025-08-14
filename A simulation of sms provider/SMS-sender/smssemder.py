# -*- coding: utf-8 -*-
"""
Created on Sat Aug  2 20:25:24 2025

@author: (Z-ia Group) https://github.com/hesamzia
in this app i simulate a sms provider because it was hard for me to get a 
license. in this app i have a page for send an message from this app and  
localhost:5001 to other app and localhost:5000. i get message in this app from 
main app.
"""

from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_cors import CORS
import config

app = Flask(__name__)

CORS(app, resources={r"/receivesms": {"origins": "*"}})

CALL_BACK_TOKEN = config.CALL_BACK_TOKEN

@app.route("/")
def main_page():
    #This the main page of the site that redirected to /home
    return redirect(url_for('home'))

@app.route("/home")
def home():
    #This is the home page of the site 
    return render_template("index.html")

@app.route("/sendsms")
def sendsms():
    #send sms to client (SMS-Verification App) with send-message.html
    return render_template("send-message.html",call_back = CALL_BACK_TOKEN)

@app.route("/receivesms", methods = ['POST'])
def receivesms():
    #recieve sms from sms-verification app to send it to client in this 
    # instance we just give sms 
    print('Processing request...')
    print('Received request:', request.data)
    print('Is jason:', request.is_json)
    data = request.get_json()
    print('Received data:', data)
    if data :
        receptor = data['receptor']
        message = data['message']
        print(f'Must send message: "{message}" to {receptor}')
        return jsonify({'response': 'Message received!'})
    else:
        print('No message received!')
        return jsonify({'error': 'No message received!'}), 400

if __name__ == "__main__":
   app.run("localhost", 5001)