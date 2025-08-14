import re
from flask import Flask,request,session,jsonify
from dotenv import load_dotenv
import os 
from db import Database
import api as api
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flask_mail import Mail, Message
from utils import generate_otp
import random

# Load from .env file
load_dotenv()   


app = Flask(__name__)
# CORS(app, supports_credentials=True)
CORS(app, origins="http://localhost:5173", supports_credentials=True, allow_headers=["Content-Type"], methods=["GET", "POST", "OPTIONS"])

# Secret key for sessions 
app.secret_key = os.getenv("SECRET_KEY")
# app.secret_key = secret_key

# Mail Config           
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')    
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')   
  
mail = Mail(app)

# DB object 
dbo = Database()

# @app.route('/send-otp', methods=['POST'])
# def send_otp():
#     data = request.get_json()
#     email = data.get('email')
#     otp = str(random.randint(100000, 999999))
#     session['otp'] = otp
#     session['otp_email'] = email
#     msg = Message('Your OTP Code', sender=app.config['MAIL_USERNAME'], recipients=[email])
#     msg.body = f'Your OTP code is {otp}'
#     mail.send(msg)
#     return jsonify({'success': True, 'message': 'OTP sent to email.'})



@app.route('/send-otp', methods=['POST'])
def send_otp():
    # data = request.get_json()
    # email = data.get('email')
    
    email = request.json.get('email')

    otp = str(random.randint(100000, 999999))  # Generate OTP

    try:
        msg = Message(subject='Your OTP Code',
                      recipients=[email],
                      body=f'Your OTP is {otp}')
        mail.send(msg)
        return jsonify({'message': 'OTP sent successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# @app.route('/verify-otp', methods=['POST'])
# def verify_otp():
#     data = request.get_json()
#     otp = data.get('otp')
#     email = data.get('email')
#     print("Session OTP:", session.get('otp'))
#     print("Session Email:", session.get('otp_email'))
#     print("Received OTP:", otp)
#     print("Received Email:", email)
#     if otp == session.get('otp') and email == session.get('otp_email'):
#         return jsonify({'success': True, 'message': 'OTP verified.'})
#     else:
#         return jsonify({'success': False, 'message': 'Invalid OTP.'}), 400

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    user_otp = request.json.get('otp')

    if session.get('otp') == user_otp:
        session.pop('otp', None)  # Remove OTP after success
        return jsonify({'message': 'OTP verified'}), 200
    else:
        return jsonify({'error': 'Invalid OTP'}), 400


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
        # Send registration success email
        msg = Message('Registration Successful', sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f'Hello {name},\n\nYour registration was successful! You can now log in with your email: {email}.'
        mail.send(msg)
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
        session['logged_in'] = True
        return jsonify({"success": True, "message": "Login successful"})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."})


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
  
  
@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('new_password')

    # Check OTP and email match session
    if otp == session.get('otp') and email == session.get('otp_email'):
        # Password strength validation (reuse your regex)
        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not re.match(password_regex, new_password):
            return jsonify({
                "success": False,
                "message": "Password must include uppercase, lowercase, digit, special character and be at least 8 characters."
            }), 400

        hashed_password = generate_password_hash(new_password)
        # Update password in DB
        result = dbo.update_password(email, hashed_password)
        if result:
            # Optionally clear OTP from session
            session.pop('otp', None)
            session.pop('otp_email', None)
            return jsonify({"success": True, "message": "Password reset successful."})
        else:
            return jsonify({"success": False, "message": "Failed to update password."}), 500
    else:
        return jsonify({"success": False, "message": "Invalid OTP or email."}), 400
  
    
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