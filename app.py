import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from dotenv import load_dotenv
from os.path import join, dirname

# Load environment variables
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/img'
app.config['MAX_CONTENT_PATH'] = 1 * 1024 * 1024
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return secure_filename(unique_filename)

@app.route('/')
def home():
    profiles = list(db.profiles.find({}))
    return render_template('index.html', profiles=profiles)

@app.route('/add_profile', methods=['GET', 'POST'])
def add_profile():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        hobby = request.form['hobby']
        file = request.files['file']
        error = False

        if not name:
            flash('Name is required', 'error')
            error = True
        if not phone:
            flash('Phone is required', 'error')
            error = True
        if not email:
            flash('Email is required', 'error')
            error = True
        if not hobby:
            flash('Hobby is required', 'error')
            error = True
        if not file or not allowed_file(file.filename):
            flash('Valid file is required', 'error')
            error = True

        if error:
            return render_template('add_profile.html', name=name, phone=phone, email=email, hobby=hobby)

        filename = generate_unique_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        profile = {
            'name': name,
            'phone': phone,
            'email': email,
            'hobby': hobby,
            'filename': filename
        }
        result = db.profiles.insert_one(profile)
        profile['_id'] = str(result.inserted_id)
        socketio.emit('profile_update', profile)
        return redirect(url_for('home'))
    return render_template('add_profile.html')

@app.route('/edit/<profile_id>', methods=['GET', 'POST'])
def edit_profile(profile_id):
    profile = db.profiles.find_one({'_id': ObjectId(profile_id)})
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        hobby = request.form['hobby']
        file = request.files['file']
        error = False

        if not name:
            flash('Name is required', 'error')
            error = True
        if not phone:
            flash('Phone is required', 'error')
            error = True
        if not email:
            flash('Email is required', 'error')
            error = True
        if not hobby:
            flash('Hobby is required', 'error')
            error = True
        if file and not allowed_file(file.filename):
            flash('Valid file is required', 'error')
            error = True

        if error:
            return render_template('edit_profile.html', profile=profile)

        if file:
            filename = generate_unique_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], profile['filename']))
        else:
            filename = profile['filename']

        profile_update = {
            'name': name,
            'phone': phone,
            'email': email,
            'hobby': hobby,
            'filename': filename
        }
        db.profiles.update_one({'_id': ObjectId(profile_id)}, {'$set': profile_update})
        profile_update['_id'] = profile_id
        socketio.emit('profile_edit', profile_update)
        return redirect(url_for('home'))
    return render_template('edit_profile.html', profile=profile)

@app.route('/delete/<profile_id>', methods=['POST'])
def delete_profile(profile_id):
    profile = db.profiles.find_one({'_id': ObjectId(profile_id)})
    if profile:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], profile['filename']))
        db.profiles.delete_one({'_id': ObjectId(profile_id)})
        socketio.emit('profile_delete', {'profile_id': profile_id})
        flash('Profile successfully deleted')
    return redirect(url_for('home'))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
