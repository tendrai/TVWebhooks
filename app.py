from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, this is the home page!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(data)  # Log the received data
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
