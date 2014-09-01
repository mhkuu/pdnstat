import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug import secure_filename
import pdn
from pdnstat import check_relation

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['pdn'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024

@app.route("/")
def do():
    return "Hello World!"

@app.route('/hello/')
def hello():
    return render_template('template.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            games = pdn.loads(file.read())
            #results = check_relation(games)
            first = pdn.dumps(games[0])
            print first
            return render_template('template.html', game = first)
            #return redirect(url_for('uploaded_file', filename=filename))
    return render_template('upload.html')
    
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
if __name__ == "__main__":
    app.debug = True
    app.run()