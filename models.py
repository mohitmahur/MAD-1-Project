from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()




# .........................models.............................................




class User(db.Model):
    __tablename__= 'user'
    u_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    _password = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(20), nullable=True)
    creator=db.Column(db.Boolean, default=False)
    black_creator=db.Column(db.Boolean, default=False)
    is_admin=db.Column(db.Boolean, nullable = False , default = False)
    songs = db.relationship('Song', backref='owner', lazy=True)


    @property
    def password(self):
        raise AttributeError('Not Readable')
    
    
    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)
    

    def check_pass(self, password):
        return check_password_hash(self._password , password)
    
    



class Song(db.Model):
    __tablename__ = 'song'
    id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(40), nullable=False)
    c_name=db.Column(db.String(60), nullable=False)               #creator name...................
    album_id=db.Column(db.Integer, db.ForeignKey('album.id'))
    lyrics=db.Column(db.String, nullable=False)
    duration=db.Column(db.Integer, nullable=False)
    genre=db.Column(db.String(80), nullable=False)
    r_date=db.Column(db.Date, nullable=False)
    filename=db.Column(db.String(255), nullable=False)
    artist_name=db.Column(db.String, nullable=False)
    likes=db.Column(db.Integer, default=0)
    dislikes=db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.u_id'))
    user = db.relationship('User', back_populates='songs' , overlaps='owner')

    

    


class Album(db.Model):
    __tablename__='album'
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String, unique=True ,nullable=False)
    c_name=db.Column(db.String, nullable=False)
    year=db.Column(db.Date, nullable=True)
    songs=db.relationship('Song', backref='album', lazy=True )
    




# Many-to-Many relation between playlist and song.......................


playlist_song_table = db.Table('playlist_song', 
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'), primary_key=True)                          
)

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.u_id'), nullable=False)
    songs = db.relationship('Song', secondary=playlist_song_table, backref='playlists', lazy=True, primaryjoin=(id == playlist_song_table.c.playlist_id))










