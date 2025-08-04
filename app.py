
from flask import Flask, request,jsonify
import requests
from flask_cors import CORS

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

def check_serial():
    pass

if __name__ == "__main__":
   app.run("localhost", 5000, debug=True)
#txt = main_page()

#print(txt)


