import os
import socket
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, render_template, redirect, send_file, url_for, send_from_directory
app = Flask(__name__)
UPLOAD_FOLDER = './files'
ip = socket.gethostbyname(socket.gethostname())


def byte_units(value, units=-1):
    UNITS = ('Bytes', 'KB', 'MB', 'GB', 'TB', 'EB', 'ZB', 'YB')
    i = 1
    value /= 1000.0
    while value > 1000 and (units == -1 or i < units) and i+1 < len(UNITS):
        value /= 1000.0
        i += 1
    return f'{round(value,3):.3f} {UNITS[i]}'


app.jinja_env.filters.update(byte_units=byte_units)


def get_files(target):
    for file in os.listdir(target):
        path = os.path.join(target, file)
        if os.path.isfile(path):
            yield (
                file,
                datetime.utcfromtimestamp(os.path.getmtime(path)),
                os.path.getsize(path)
            )


@app.route('/')
def main():
    return render_template('./index.html')


@app.route('/upload')
def upload():
    return render_template('./upload.html')


@app.route('/howtouse')
def howtouse():
    return render_template('./howtouse.html')


@app.route('/api/upload', methods=['GET', 'POST'])
def uploadFile():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
    file = request.files['file']
    filename = request.form['filename'].replace(" ", "_")
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file:
        if filename == '':
            filename = secure_filename(file.filename.replace(" ", "_"))
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(request.url)


@app.route('/download')
def download():
    files = get_files(app.config['UPLOAD_FOLDER'])
    return render_template('./download.html', files=files)


@app.route('/api/download/<path:filename>', methods=['GET', 'POST'])
def downloadfile(filename):
    file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(file, as_attachment=True)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.run(host=ip, port=4444, debug=True, use_reloader=True)
