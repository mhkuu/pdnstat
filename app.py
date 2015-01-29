# Flask
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from werkzeug import secure_filename
from flask.ext.sqlalchemy import SQLAlchemy
import sqlite3
# PDN-related
import pdn
from pdnstat import hamming_distance
# Python standard libraries
from collections import Counter
import os

#####
# Configuration
#####

app = Flask(__name__)
app.config.update(dict(
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'p.db'),
    DEBUG = True,
    SECRET_KEY = 'development key',
    USERNAME = 'admin',
    PASSWORD = 'default',
    UPLOAD_FOLDER = 'uploads/',
    ALLOWED_EXTENSIONS = set(['pdn']),
    MAX_CONTENT_LENGTH = 500 * 1024
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
    nr = db.Column(db.Integer)
    author = db.Column(db.String(200))
    source = db.Column(db.String(200))
    year = db.Column(db.Integer)
    pdn = db.Column(db.Text)
    fen_string = db.Column(db.String(100))

    def __init__(self, collection, nr, author, source, year, pdn, fen_string):
        self.collection = collection
        self.nr = nr
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
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'))
    collection = db.relationship('Collection', foreign_keys='Distance.collection_id', backref=db.backref('distances', lazy='dynamic'))
    game1_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game1 = db.relationship('Game', foreign_keys='Distance.game1_id')
    game2_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game2 = db.relationship('Game', foreign_keys='Distance.game2_id')
    distance = db.Column(db.Integer)

    def __init__(self, collection, game1, game2, distance):
        self.collection = collection
        self.game1 = game1
        self.game2 = game2
        self.distance = distance

    def __repr__(self):
        return '<Distance %r>' % self.distance

        
#####
# Error handlers
#####

@app.errorhandler(413)
def request_entity_too_large(error):
    return render_template('upload.html', error='Bestand te groot')

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
def collection(collection_name):
    c = Collection.query.filter_by(name=collection_name).first_or_404()
    g = c.games.all()
    d = c.distances.all()

    gn = list() 
    d_data = list() 
    for distance in d: 
        dd1 = [distance.game1.nr, distance.game2.nr, distance.distance] 
        dd2 = [distance.game2.nr, distance.game1.nr, distance.distance] 
        d_data.append(dd1)
        d_data.append(dd2)
        
    for game in g:
        dd = [game.nr, game.nr, 0] 
        d_data.append(dd)
        gn.append(str(game))
        
    return render_template('collection.html', collection=c, games=g, distances=d, data=year_graph(g), game_names=gn, d_data=d_data)
    
@app.route('/game/<game_id>')
def game(game_id):
    return render_template('game.html', game=Game.query.get_or_404(game_id))
    
@app.route('/distance/<distance_id>')
def distance(distance_id):
    return render_template('distance.html', distance=Distance.query.get_or_404(distance_id))

@app.route('/upload/', methods=['GET', 'POST'])
def upload_pdn():
    if request.method == 'POST':
        error = None
        f = request.files['file']
        if not f: 
            error = 'Geen bestand geselecteerd'
        elif not allowed_file(f.filename):
            error = 'Bestand niet geaccepteerd'
        else: 
            filename = secure_filename(f.filename)
            #f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            collection_name = request.form['name'].lower()
            if not collection_name: 
                error = 'Geen naam opgegegeven'
            else: 
                c = Collection.query.filter_by(name=collection_name).first()
                if c: 
                    error = 'Naam is al in gebruik: verzin een andere naam!'
                else: 
                    upload_file(f, collection_name)
                    return redirect(url_for('collection', collection_name=collection_name))
        return render_template('upload.html', error=error)
    else: 
        return render_template('upload.html')
    
#####
# Helpers
#####

def upload_file(f, collection_name):
    c = Collection(collection_name)
    db.session.add(c)
    db.session.commit()
    
    gs = list()
    games = pdn.loads(f.read())
    for n, game in enumerate(games): 
        year = None
        if game.date != '?':
            year = game.date[:4]
        g = Game(c, n, game.white, game.event, year, unicode(game.dumps(), 'utf-8'), game.fen_string)
        db.session.add(g)
        gs.append(g)
    
    db.session.commit()
    results = check_relation(gs)
    
    for result in results: 
        d = Distance(c, result[0], result[1], result[2])
        db.session.add(d)
    
    db.session.commit()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in (app.config['ALLOWED_EXTENSIONS'])
        
def check_relation(games): 
    result = list()
    for n, game1 in enumerate(games):
        for game2 in games[n+1:]:
            d = hamming_distance(game1.fen_string, game2.fen_string)
            #if d < 10: 
            result.append([game1, game2, d])
    return result

def year_graph(games): 
    years = list() 
    for game in games:
        if game.year:
            years.append(game.year)
    return sorted(Counter(years).items())
    
#####
# Main
#####
    
if __name__ == '__main__':
    app.run()