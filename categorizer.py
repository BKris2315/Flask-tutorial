from flask import Flask, render_template, request, redirect, flash, url_for, send_from_directory, after_this_request
import numpy as np
from PIL import Image
from keras.models import load_model
from werkzeug.utils import secure_filename
import os
import urllib.request
# from temp import tempfile
# from celery_tasks import cleanup_task
app = Flask(__name__)
app.config.from_object('celeryconfig')
model = load_model('traffic_sign_categorizer.h5')
classes = {1: 'A - No right, left, or U-turn',
           2: 'B - Speed limits',
           3: 'C - Road closed',
           4: 'D - No entry',
           5: 'E - No stopping, no parking',
           6: 'F - Other types of prohibitory traffic signs'}


UPLOAD_FOLDER = 'static/uploads/'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def remove_uploaded_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.remove(file_path)
    except Exception as error:
        app.logger.error("Error deleting uploaded file: {}".format(error))

def remove_temporary_file(temp_file):
    try:
        temp_file.close()
        os.remove(temp_file.name)
    except Exception as error:
        app.logger.error("Error deleting temporary file: {}".format(error))

from flask import session
import uuid

def remove_user_folder(user_folder):
    try:
        os.rmdir(user_folder)
        print(f"User folder {user_folder} removed successfully.")
    except Exception as error:
        app.logger.error("Error deleting user folder: {}".format(error))

def generate_session_token():
    return str(uuid.uuid4())

@app.route('/')
def index():
    if 'user_id' not in session:
        session['user_id'] = generate_session_token()

    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify():
    
    # user_folder = os.path.join(app.config['UPLOAD_FOLDER'], session['user_id'])
    user_folder = app.config['UPLOAD_FOLDER']

    # Create user-specific folder if it doesn't exist
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    # Remove files from the user's folder
    for filename in os.listdir(user_folder):
        file_path = os.path.join(user_folder, filename)
        try:
            os.remove(file_path)
            print(f"File {file_path} removed successfully.")
        except Exception as e:
            print(f"Error removing file {file_path}: {e}")

    if 'file_path' not in request.files:
        return render_template('index.html', sign='Error: No file part')

    file = request.files['file_path']

    if file.filename == '':
        return render_template('index.html', sign='Error: No selected file')

    if file:
        try:
            # Save the file to the server
            filename = secure_filename(file.filename)
            file_path = os.path.join(user_folder, filename)
            file.save(file_path)
            flash('Image successfully uploaded and displayed below')

            # Process the image file
            image = Image.open(file_path).resize((125, 125))
            image = np.expand_dims(np.array(image), axis=0)
            pred_probs = model.predict(image)
            pred_class = np.argmax(pred_probs)
            sign = classes.get(pred_class + 1, 'Unknown Sign')

            # image_path = url_for('uploaded_image', filename=filename)
            print("File saved to:", file_path)
            # print("Image path:", image_path)
            
            return render_template('index.html', sign=sign, filename=file_path)
        except Exception as e:
            print("Error processing image:", e)
            return render_template('index.html', sign='Error: Failed to process image')

@app.route('/<filename>')
def display_image(filename):
    print('uploads/'+ str(session['user_id']) + filename)
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/'+ str(session['user_id']) + filename), code=301)

# Use the teardown_request hook to remove the user folder after the request
@app.teardown_request
def teardown_request(exception=None):
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], session.get('user_id', ''))
    if user_folder and os.path.exists(user_folder):
        remove_user_folder(user_folder)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888)
