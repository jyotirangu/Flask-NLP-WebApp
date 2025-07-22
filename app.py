from flask import Flask,render_template,request,redirect,session
from db import Database
import api

app = Flask(__name__)
app.secret_key = '9f3d2c7b8a4e1c6e4d5f1a2b3c4d6e7f'  # REQUIRED for session to work
dbo = Database()


@app.route('/') 
def index():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/perform_registration', methods=['post'])
def perform_registration():
    name = request.form.get('user_name')
    email = request.form.get('user_email')
    password = request.form.get('user_password')
    
    response = dbo.insert(name, email, password)
    
    if response:
        return render_template('login.html', message="Registration Successful. Kindly Login to proceed")
    else:
        return render_template('register.html', message="email already exists")
    
@app.route('/perform_login', methods=['post'])
def perform_login():
    email = request.form.get('user_email')
    password = request.form.get('user_password')
    
    response = dbo.search(email, password)
    
    if response:
        session['logged_in'] = True
        return redirect('/profile')
    else:
        return render_template('login.html', message='Incorrect email/password')
    
    
@app.route('/profile')
def profile():
    if session.get('logged_in'):
        return render_template('profile.html')
    else:
        return redirect('/')

@app.route('/ner')
def ner():
    if session.get('logged_in'):
        return render_template('ner.html')
    else:
        return redirect('/')

@app.route('/perform_ner',methods=['post'])
def perform_ner():
    if session.get('logged_in'):
        text = request.form.get('ner_text')
        response = api.ner(text)
        print(response)
        return render_template('ner.html', response=response)
    else:
        return redirect('/')
    
@app.route('/sentiment_analysis')
def sentiment_analysis():
    if session.get('logged_in'):
        return render_template('sentiment_analysis.html')
    else:
        return redirect('/')
    
@app.route('/perform_sentiment_analysis', methods=['post'])
def perform_sentiment_analysis():
    if session.get('logged_in'):
        text = request.form.get('sentiment_text')
        response = api.sentiment_analysis(text)
        polarity = response.polarity
        subjectivity = response.subjectivity

        return render_template('sentiment_analysis.html', polarity=polarity, subjectivity=subjectivity)
    else:
        return redirect('/')
    
@app.route('/emotion_detection')
def emotion_detection():
    if session.get('logged_in'):
        return render_template('emotion_detection.html')
    else:
        return redirect('/')
    
@app.route('/perform_emotion_detection', methods=['post'])
def perform_emotion_detection():
    if session.get('logged_in'):
        text = request.form.get('emotion_text')
        
        if not text:  # check if None or empty
            return render_template('emotion_detection.html', result="Please enter some text.")
        
        response = api.emotion_detection(text)
        print(response)
        return render_template('emotion_detection.html', response=response)
    else:
        return redirect('/')
    

app.run(debug=True)

