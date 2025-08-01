
from flask import Flask


app = Flask(__name__)

@app.route("/")
def main_page():
    '''This the main page of the site
    '''
    print("Hello, Flask!")
    return "Hello, Flask!!"

if __name__ == "__main__":
   app.run()
txt = main_page()

print(txt)


