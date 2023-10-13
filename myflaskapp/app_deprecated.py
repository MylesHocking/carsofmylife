from flask import Flask, render_template, request, jsonify
from api import api  # Import the Blueprint
import requests

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')  # Register the Blueprint

@app.route('/')
def index():
    print("Index function triggered.")  # Debugging print statement
    return render_template('index.html')

@app.route('/verify_google_token', methods=['POST'])
def verify_google_token():
    received_data = request.json
    token = received_data.get('token', '')

    GOOGLE_TOKEN_INFO_URL = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"

    response = requests.get(GOOGLE_TOKEN_INFO_URL)
    token_info = response.json()

    if "error_description" in token_info:
        return jsonify({"status": "failure", "message": "Invalid token"}), 401
    
    return jsonify({"status": "success", "message": "Valid token", "user_info": token_info}), 200

if __name__ == '__main__':
    app.run(debug=True)
