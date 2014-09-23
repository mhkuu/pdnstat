import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from werkzeug import secure_filename
import pdn
import sqlite3
from pdnstat import hamming_distance
from flask.ext.sqlalchemy import SQLAlchemy

#####
# Configuration
#####

app = Flask(__name__)
app.config.update(dict(
#    DATABASE = os.path.join(app.root_path, 'p.db'),
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'p.db'),
    DEBUG = True,
    SECRET_KEY = 'development key',
    USERNAME = 'admin',
    PASSWORD = 'default',
    UPLOAD_FOLDER = 'uploads/',
    ALLOWED_EXTENSIONS = set(['pdn']),
    MAX_CONTENT_LENGTH = 100 * 1024
)) 
db = SQLAlchemy(app)

#####
# Models
#####

class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Collection %r>' % self.name

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'))
    collection = db.relationship('Collection', foreign_keys='Game.collection_id', backref=db.backref('games', lazy='dynamic'))
    author = db.Column(db.String(200))
    source = db.Column(db.String(200))
    year = db.Column(db.Integer)
    pdn = db.Column(db.Text)
    fen_string = db.Column(db.String(100))

    def __init__(self, c, author, source, year, pdn, fen_string):
        self.collection = c
        self.author = author
        self.source = source
        self.year = year
        self.pdn = pdn
        self.fen_string = fen_string

    def __repr__(self):
        return '<Game %r>' % (self.id)
        
    def __str__(self):
        return '%s (%s)' % (self.author, self.year if self.year else '?')
        
class Distance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game1_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game1 = db.relationship('Game', foreign_keys='Distance.game1_id')
    game2_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game2 = db.relationship('Game', foreign_keys='Distance.game2_id')
    distance = db.Column(db.Integer)

    def __init__(self, game1, game2, distance):
        self.game1 = game1
        self.game2 = game2
        self.distance = distance

    def __repr__(self):
        return '<Distance %r>' % self.distance

#####
# Routes
#####
        
@app.route('/')
def home():
    return render_template('home.html') 
    
@app.route('/collections/')
def show_collections():
    return render_template('show_collections.html', collections=Collection.query.all())
    
@app.route('/<collection_name>/')
def show(collection_name):
    c = Collection.query.filter_by(name=collection_name).first_or_404()
    g = c.games.all()
    d = Distance.query.all() # FIXME
    return render_template('show.html', collection=c, games=g, distances=d)
    
@app.route('/game/<game_id>')
def game(game_id):
    return render_template('game.html', game=Game.query.get_or_404(game_id))

@app.route('/upload/', methods=['GET', 'POST'])
def upload_pdn():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            c = Collection(request.form['name'].lower())
            db.session.add(c)
            db.session.commit()
            
            gs = list()
            games = pdn.loads(file.read())
            for game in games: 
                year = None
                if game.date != '?':
                    year = game.date[:4]
                g = Game(c, game.white, game.event, year, game.dumps(), game.fen_string)
                db.session.add(g)
                gs.append(g)
            
            db.session.commit()
            results = check_relation(gs)
            
            for result in results: 
                d = Distance(result[0], result[1], result[2])
                db.session.add(d)
            
            db.session.commit()
            flash('File was successfully handled')
            return redirect(url_for('show', collection_name=c.name))
    else: 
        return render_template('upload.html')
        
#####
# Helpers
#####

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in (app.config['ALLOWED_EXTENSIONS'])
        
def check_relation(games): 
    result = list()
    for n, game1 in enumerate(games):
        for game2 in games[n+1:]:
            d = hamming_distance(game1.fen_string, game2.fen_string)
            #if d < 10: 
            result.append([game1, game2, d])
    return result

#####
# Main
#####
    
if __name__ == '__main__':
    app.run()