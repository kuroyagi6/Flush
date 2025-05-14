from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_talisman import Talisman
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
Talisman(app)  # Enforce HTTPS and basic security headers

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'webm'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static/thumbnails', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "default-src 'self';"
    return response

@app.route('/')
def index():
    videos = []
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if allowed_file(filename):
                base_name = os.path.splitext(filename)[0]
                jpg_thumb = f'static/thumbnails/{base_name}.jpg'
                png_thumb = f'static/thumbnails/{base_name}.png'

                if os.path.exists(jpg_thumb):
                    thumbnail = 'thumbnails/' + base_name + '.jpg'
                elif os.path.exists(png_thumb):
                    thumbnail = 'thumbnails/' + base_name + '.png'
                else:
                    thumbnail = 'thumbnails/default.jpg'

                videos.append({'name': filename, 'thumbnail': thumbnail})
    return render_template('index.html', videos=videos)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'video' not in request.files:
            return 'No file part', 400
        file = request.files['video']
        if file.filename == '':
            return 'No selected file', 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return redirect(url_for('index'))
        else:
            return 'Invalid file type', 400
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/video/<filename>')
def video(filename):
    return render_template('video.html', filename=filename)

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    results = []
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if allowed_file(filename) and query in filename.lower():
                base_name = os.path.splitext(filename)[0]
                jpg_thumb = f'static/thumbnails/{base_name}.jpg'
                png_thumb = f'static/thumbnails/{base_name}.png'

                if os.path.exists(jpg_thumb):
                    thumbnail = 'thumbnails/' + base_name + '.jpg'
                elif os.path.exists(png_thumb):
                    thumbnail = 'thumbnails/' + base_name + '.png'
                else:
                    thumbnail = 'thumbnails/default.jpg'

                results.append({'name': filename, 'thumbnail': thumbnail})
    return render_template('index.html', videos=results)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
