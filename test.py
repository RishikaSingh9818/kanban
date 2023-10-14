from main import Flask
app = Flask(__name__)

@app.route('/landingpage',methods=["GET"])
def hello_world(value):
    return "working"




if __name__ == '__main__':
   app.run(debug=True)