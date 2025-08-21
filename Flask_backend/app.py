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
import time
from flask import make_response

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


# ===== Unified responses =====
# from flask import make_response

def ok(message, data=None, status=200):
    return make_response(jsonify({"success": True, "message": message, "data": data or {}}), status)

def err(message, status=400):
    return make_response(jsonify({"success": False, "message": message}), status)

# ===== OTP settings =====
OTP_TTL_SECONDS = 300          # 5 minutes
OTP_RATE_LIMIT_SECONDS = 60    # 1 minute between sends
SESSION_KEY_OTP = "otp"
SESSION_KEY_OTP_EMAIL = "otp_email"
SESSION_KEY_OTP_EXPIRES = "otp_expires"
SESSION_KEY_OTP_SENT_AT = "otp_sent_at"


@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json(silent=True) or {}
    email = data.get('email')
    if not email:
        return err("Email is required.", 400)

    # Basic email sanity check (reuse your regex if you prefer)
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return err("Invalid email format.", 400)

    # Rate limit
    now = int(time.time())
    last_sent = session.get(SESSION_KEY_OTP_SENT_AT, 0)
    if now - last_sent < OTP_RATE_LIMIT_SECONDS:
        return err(f"Please wait {OTP_RATE_LIMIT_SECONDS - (now - last_sent)}s before requesting another OTP.", 429)

    # Generate OTP (use your utils.generate_otp if it exists)
    try:
        otp = generate_otp()  # should return a 6-digit string
    except Exception:
        # fallback if your utils isn't ready
        otp = str(random.randint(100000, 999999))

    # Persist in session
    session[SESSION_KEY_OTP] = otp
    session[SESSION_KEY_OTP_EMAIL] = email
    session[SESSION_KEY_OTP_EXPIRES] = now + OTP_TTL_SECONDS
    session[SESSION_KEY_OTP_SENT_AT] = now
    session.modified = True

    # Send mail
    try:
        msg = Message(
            subject='Your OTP Code',
            recipients=[email],
            body=f'Your OTP is {otp}. It expires in {OTP_TTL_SECONDS // 60} minutes.'
        )
        mail.send(msg)
        return ok("OTP sent successfully.", {"ttl_seconds": OTP_TTL_SECONDS})
    except Exception as e:
        # If email fails, clear OTP from session so state isn't dangling
        for k in (SESSION_KEY_OTP, SESSION_KEY_OTP_EMAIL, SESSION_KEY_OTP_EXPIRES):
            session.pop(k, None)
        return err(f"Failed to send OTP: {str(e)}", 500)


@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json(silent=True) or {}
    user_email = data.get('email')
    user_otp = data.get('otp')

    if not user_email or not user_otp:
        return err("OTP is required.", 400)

    stored_otp = session.get(SESSION_KEY_OTP)
    stored_email = session.get(SESSION_KEY_OTP_EMAIL)
    expires_at = session.get(SESSION_KEY_OTP_EXPIRES, 0)

    if not stored_otp or not stored_email:
        return err("No OTP found. Please request a new one.", 400)

    if int(time.time()) > int(expires_at):
        # Clear expired OTP
        for k in (SESSION_KEY_OTP, SESSION_KEY_OTP_EMAIL, SESSION_KEY_OTP_EXPIRES):
            session.pop(k, None)
        return err("OTP expired. Please request a new one.", 400)

    if user_email != stored_email or user_otp != stored_otp:
        return err("Invalid OTP or email.", 400)

    # # Success -> clear OTP
    # for k in (SESSION_KEY_OTP, SESSION_KEY_OTP_EMAIL, SESSION_KEY_OTP_EXPIRES):
    #     session.pop(k, None)
    
        # ✅ Don't clear OTP here — just mark it as verified
    session["otp_verified"] = True

    return ok("OTP verified.")




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




@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == "OPTIONS":
        return jsonify({"message": "Preflight OK"}), 200

    data = request.get_json(silent=True) or {}
    name = data.get('user_name')
    email = data.get('user_email')
    password = data.get('user_password')

    if not all([name, email, password]):
        return err("All fields are required.", 400)
     
    EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(EMAIL_REGEX, email):
        return err("Invalid email format ❌", 400)
    
    # ✅ Check OTP verified before registering
    if not session.get("otp_verified") or session.get("otp_verified") is not True:
        return err("Please verify your email with OTP before registering ❌", 400)
    
    # ✅ Check OTP email == registration email
    if session.get("otp_email") != email:
        return err("OTP was not verified for this email ❌", 400)


    # Hash the password
    hashed_password = generate_password_hash(password)

    # Insert into DB
    result = dbo.insert(name, email, hashed_password)

    if result == 1:
        # ✅ Clear OTP state after successful registration
        for k in ("otp_verified", "otp_email", "otp", "otp_expires"):
            session.pop(k, None)

        
        return jsonify({
            "success": True,
            "message": "User registered successfully. Please login now."
        }), 200
    else:
        return err("Email already exists ❌", 400)




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
    data = request.get_json(silent=True) or {}
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('new_password')

    if not all([email, otp, new_password]):
        return err("Email, OTP, and new_password are required.", 400)


    # ✅ Check OTP verification status
    if not session.get("otp_verified"):
        return err("OTP not verified.", 400)
    
    stored_otp = session.get(SESSION_KEY_OTP)
    stored_email = session.get(SESSION_KEY_OTP_EMAIL)
    expires_at = session.get(SESSION_KEY_OTP_EXPIRES, 0)

    if not stored_otp or not stored_email:
        return err("No OTP found. Please request a new one.", 400)

    if int(time.time()) > int(expires_at):
        for k in (SESSION_KEY_OTP, SESSION_KEY_OTP_EMAIL, SESSION_KEY_OTP_EXPIRES):
            session.pop(k, None)
        return err("OTP expired. Please request a new one.", 400)

    if otp != stored_otp or email != stored_email:
        return err("Invalid OTP or email.", 400)

    # Password strength validation 
    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    if not re.match(password_regex, new_password):
        return err("Password must include uppercase, lowercase, digit, special char and be at least 8 chars.", 400)

    try:
        hashed_password = generate_password_hash(new_password)
        result = dbo.update_password(email, hashed_password)
        if not result:
            return err("Failed to update password.", 500)

        # ✅ Clear everything after success
        for k in (SESSION_KEY_OTP, SESSION_KEY_OTP_EMAIL, SESSION_KEY_OTP_EXPIRES, "otp_verified"):
            session.pop(k, None)

        return ok("Password reset successful.")
    except Exception as e:
        return err(f"Internal error: {str(e)}", 500)
 
    
    
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