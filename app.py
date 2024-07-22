from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(data)
    # Add your logic to handle the webhook data
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
