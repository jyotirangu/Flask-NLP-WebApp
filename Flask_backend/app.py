import re
from flask import Flask,request,session,jsonify
from dotenv import load_dotenv
import os 
from db import Database
import api as api
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash



from flask_cors import CORS
app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

CORS(app, origins="http://localhost:5173", supports_credentials=True, allow_headers=["Content-Type"], methods=["GET", "POST", "OPTIONS"])


load_dotenv()    # Load from .env file
# Now you can access them like this:
secret_key = os.getenv("SECRET_KEY")
app.secret_key = secret_key
dbo = Database()


@app.route('/') 
def home():
    return {'message': 'Hello from Flask backend!'}

@app.route('/session-check')
def session_check():
    return jsonify({'logged_in': session.get('logged_in', False)})


@app.route('/api/register', methods=['POST'])
def perform_registration():
    data = request.get_json()
    name = data.get('user_name')
    email = data.get('user_email')
    password = data.get('user_password')

    # Email format validation
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, email):
        return jsonify({"success": False, "message": "Invalid email format."}), 400

    # Password strength validation
    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    if not re.match(password_regex, password):
        return jsonify({
            "success": False,
            "message": "Password must include uppercase, lowercase, digit, special character and be at least 8 characters."
        }), 400

    hashed_password = generate_password_hash(password)
    # Insert into DB
    response = dbo.insert(name, email, hashed_password)

    if response:
        return jsonify({"success": True, "message": "Registration successful."})
    else:
        return jsonify({"success": False, "message": "Email already exists."}), 409



@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({"message": "Preflight OK"}), 200  # Optional but safe
    
    data = request.get_json()
    email = data.get('user_email')
    password = data.get('user_password')

    user = dbo.get_user_by_email(email)
    if user and check_password_hash(user["password"], password):
        session['user_email'] = user["email"]
        return jsonify({"success": True, "message": "Login successful"})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401



@app.route('/perform_ner', methods=['POST'])
def perform_ner():
    if session.get('logged_in'):
        try:
            data = request.get_json()
            text = data.get('ner_text', '')
            response = api.ner(text)
            return jsonify(response)
        except Exception as e:
            print("Error:", e)
            return jsonify({"error": "Internal server error"}), 500
    else:
        return jsonify({'error': 'Unauthorized'}), 401
    
    
@app.route('/perform_sentiment_analysis', methods=['POST'])
def perform_sentiment_analysis():
    if session.get('logged_in'):
        text = request.json.get('text')
        response = api.sentiment_analysis(text)
        return jsonify({
            "polarity": response.polarity,
            "subjectivity": response.subjectivity
        })
    else:
        return jsonify({"error": "Unauthorized"}), 401    

@app.route('/perform_emotion_detection', methods=['POST'])
def perform_emotion_detection():
    if session.get('logged_in'):
        text = request.json.get('text')
        if not text:
            return jsonify({"error": "No text provided"}), 400

        results = api.emotion_detection(text)  # List of dicts like [{'label': 'joy', 'score': 0.95}, ...]
        return jsonify(results)
    else:
        return jsonify({"error": "Unauthorized"}), 401

app.run(debug=True)