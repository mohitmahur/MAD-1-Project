from flask import Flask, render_template, request, url_for, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Song, Album , Playlist
import os
from functools import wraps
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import send_file



app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'templates/static/audios'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///song.sqlite3"




db.init_app(app)
app.app_context().push()




# ..............checking for admin login........................../..................


admin = User.query.filter_by(is_admin=True).first()
if not admin:
    admin = User(username='admin', password = 'admin', is_admin=True)
    db.session.add(admin)
    db.session.commit()





# ......................................creator..........................................
    
@app.route('/make_creator/<int:user_id>', methods=['GET'])
def make_creator(user_id):
    user = User.query.get(user_id)
    if user:
        user.creator = True
        session['user_id'] = user.u_id
        db.session.commit()
        return redirect(url_for('creator'))



@app.route('/creator')
def creator():
    user=User.query.get(session['user_id'])
    
    if user.creator==False:
        flash('You Are Not A creator')
        return redirect(url_for('play'))
    
    song=Song.query.all()
    return render_template('creator.html' , songss=song , user=user)




@app.route('/allcreators')
def creators_white():
    return render_template('allcreatorwhite.html', users=User.query.filter_by(creator=True).all())


@app.route('/black')
def creators_black():
    return render_template('allcreatorblack.html', users=User.query.filter_by(black_creator=True).all())






@app.route('/creator/blacklist/<int:user_id>')
def blacklist_creator(user_id):
    user=User.query.get(user_id)
    return render_template('black_creator.html', user=user)


@app.route('/creator/blacklist/<int:user_id>', methods=['POST'])
def blacklist_creator_post(user_id):
    user=User.query.get(user_id)
    if user.black_creator:
        flash('Creator is Already Black Creator.')
        return redirect(url_for('adminIndex'))
    user.creator=False
    user.black_creator = True
    db.session.commit()
    flash('Creator BlackListed Successfully')
    return redirect(url_for('adminIndex'))


@app.route('/creator/whitelist_creator/<int:user_id>')
def whitelist_creator(user_id):
    user=User.query.get(user_id)
    return render_template('white_creator.html', user=user)



@app.route('/creator/whitelist_creator/<int:user_id>', methods=['POST'])
def whitelis_creator_post(user_id):
    user=User.query.get(user_id)
    if not user.black_creator:
        user.creator=True
        flash('Creator is Already WhiteListed')
        return redirect(url_for('adminIndex'))
    user.black_creator = False
    user.creator=True
    db.session.commit()
    flash('Creator is Now Longer Blacklist Ceator')
    return redirect(url_for('adminIndex'))
  


@app.route('/creator/delete/<int:user_id>')
def delete_creator(user_id):
    user=User.query.get(user_id)
    songs=Song.query.filter_by(c_name=user.username).all()
    return render_template('delete_creator.html', user=user)


@app.route('/creator/delete/<int:user_id>', methods=['POST'])
def delete_creator_post(user_id):
    user=User.query.get(user_id)
    songs=Song.query.filter_by(c_name=user.username).all()
    for song in songs:
        db.session.delete(song)
        albums=Album.query.filter_by(c_name=user.username).all()
    for album in albums:
        db.session.delete(album)
    user.creator=False
    db.session.commit()
    flash('Creator Deleted Successfully.')
    return redirect(url_for('adminIndex'))







# ...............................main pages...........................................

@app.route('/')
def index():
    return render_template('index.html')


# /......................................admin routes ...........................



@app.route('/admin')
def admin():
    user=User.query.all()
    return render_template('adminlogin.html')



@app.route('/admin', methods=['POST'])
def adm():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == '' or password == '':
        flash('Username and password not empty')
        return redirect(url_for('admin'))

    user = User.query.filter_by(username=username).first()

    if not user:
        flash('Please check your login details')
        return redirect(url_for('admin'))

    if not user.check_pass(password):
        flash('Password Not Correct')
        return redirect(url_for('admin'))

    session['user_id'] = user.u_id

    if user.is_admin:
        return redirect(url_for('adminIndex'))
    else:
        flash('You have not right permission to be an Admin')
        return redirect(url_for('login'))
    



@app.route('/adminIndex')
def adminIndex():
    songs=Song.query.all()
    all_songs=len(Song.query.all())
    all_users=len(User.query.all())-1
    all_albums=len(Album.query.all())
    all_playlist=len(Playlist.query.all())
    all_creators=len(User.query.filter_by(creator=True).all())
    
    return render_template('admin.html', user=User.query.all(), all_albums=all_albums , all_playlist=all_playlist, all_songs=all_songs, all_users=all_users, all_creators=all_creators)






# .....................Login routes ..................................................



@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def log():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == '' or password == '':
        flash('Username and password not empty')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=username).first()

    if not user:
        flash('Please check your login details')
        return redirect(url_for('login'))

    if not user.check_pass(password):
        flash('Password Not Correct')
        return redirect(url_for('login'))

    session['user_id'] = user.u_id

    if user.is_admin:
        return redirect(url_for('admin'))
    elif user.creator:
        return redirect(url_for('creator'))
    else:
        return redirect(url_for('play'))
    
    


# ..........................register routes ...............................................


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def reg():
    username=request.form.get('username')
    password=request.form.get('password')
    name=request.form.get('name')

    if username == '' or password == '':
        flash('fill the username and password ', 'error')
        return redirect(url_for('register'))
    if User.query.filter_by(username=username).first():
        flash('User Already Exist Try Differnt Username', 'error')
        return redirect(url_for('register'))
    
    user = User(username=username, password=password, name=name)
    
    db.session.add(user)
    db.session.commit()
    flash('Successfully Register.', 'success')
    return redirect(url_for('login'))


# /.............................logout routes ......................................


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))
  
    




# ...................../song upload routes ..............................................



@app.route('/upload/')
def upload():
    return render_template('upload.html', user=User.query.get(session['user_id']))



@app.route('/upload', methods=['POST'])
def upload_song():
    if 'songFile' not in request.files:
        return 'No file part'
    file=request.files['songFile']
    file_path=None
    if file:
        filename=secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        



    lyrics = request.form['lyrics']
    duration = request.form['duration']
    title = request.form['title']
    r_date = request.form['releaseDate']
    artist=request.form['artist']
    c_name=request.form['c_name']
    genre=request.form['genre']


    new_date= datetime.strptime(r_date, '%Y-%m-%d').date()
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found')
        return redirect(url_for('login'))
    song=Song(title=title, duration=duration, genre=genre, c_name=c_name ,lyrics=lyrics, r_date=new_date, filename= file_path,artist_name=artist)

    db.session.add(song)
    db.session.commit()
    
    return redirect(url_for('creator'))





# ..........................play routes ............................................



@app.route('/play' )
def play():
  songs=Song.query.all()   
  return render_template('play.html', songs=songs, user=User.query.get(session['user_id']))




@app.route('/play_music/<int:song_id>', methods=['GET'])
def play_music(song_id):
    song = Song.query.get(song_id)
    if song:
        return send_file(song.filename, as_attachment=False)
    else:
        return 'Song not found'
    


# ......................./Lyrics showing route ....................................

@app.route('/lyrics/<int:song_id>', methods=['GET'])
def show_lyrics(song_id):
    song = Song.query.get(song_id)
    
    if song:
        return render_template('lyrics.html', song=song)
    else:
        return 'Lyrics Not Found'
    


# ..........................likesss....................................................
    

@app.route('/like/<int:song_id>', methods=['POST'])
def songlike(song_id):
    song=Song.query.get(song_id)
    if song:
        song.likes += 1
        db.session.commit()
    return redirect(url_for('play'))
        


@app.route('/dislike/<int:song_id>' , methods=['POST'])
def songdislike(song_id):
    song=Song.query.get(song_id)
    if song:
        song.dislikes += 1
        db.session.commit()
    return redirect(url_for('play'))
    




# ......................delete song........................................................
    

@app.route('/song/<int:id>/delete')
def delete_song(id):
    song=Song.query.get(id)
    return render_template('deletesong.html' , user=User.query.get(session['user_id']), song=Song.query.get(id))




@app.route('/song/<int:id>/delete' , methods=['POST'])
def delete_song_post(id):
    song=Song.query.get(id)
    if not song:
        flash('Song Not Exist')
        return redirect(url_for('creator'))
    db.session.delete(song)
    db.session.commit()
    flash('Song Deleted Successfully')
    return redirect(url_for('creator'))



# ........................edit song...............................................




@app.route('/song/<int:id>/edit')
def edit_song(id):
    songss=Song.query.get(id)
    return render_template('editsong.html' , user=User.query.get(session['user_id']), song=Song.query.get(id))



@app.route('/song/<int:id>/edit', methods=['POST'])
def edit_song_post(id):
    song=Song.query.get(id)
    title=request.form.get('title')
    genre=request.form.get('genre')
    year=request.form.get('year')
    duration=request.form.get('duration')
    new_year=datetime.strptime(year, '%Y-%m-%d').date()
    song.title=title
    song.genre=genre
    song.r_date=new_year
    song.duration=duration
    db.session.add(song)
    db.session.commit()
    return redirect(url_for('creator'))




# ........................album routes...................................................


@app.route('/create_album', methods=['GET', 'POST'])
def create_album():
    if request.method == 'POST':
        title = request.form['title']
        c_name = request.form['c_name']
        album = Album(title=title, c_name=c_name)
        db.session.add(album)
        db.session.commit()
        flash('Album created successfully', 'success')
        return redirect(url_for('view_albums'))
    songs=Song.query.all()
    return render_template('create_album.html', user=User.query.get(session['user_id']), songs=songs)
    


@app.route('/albums')
def view_albums():
    albums = Album.query.all()
    song=Song.query.all()
    return render_template('view_albums.html', albums=albums, songs=song ,user=User.query.get(session['user_id']))



@app.route('/album/<int:album_id>')
def view_album(album_id):
    album = Album.query.get(album_id)
    if album:
        songs=Song.query.all()
        return render_template('view_album.html', album=album, songs=songs, user=User.query.get(session['user_id']))
    else:
        return 'Album not found'




@app.route('/album/<int:id>/edit')
def edit_album(id):
    album=Album.query.get(id)
    return render_template('editalbum.html', user=User.query.get(session['user_id']), albums=Album.query.all())






@app.route('/album/<int:id>/edit', methods=['POST'])
def edit_album_post(id):
    album=Album.query.get(id)
    title=request.form.get('title')
    c_name=request.form.get('c_name')
    album.title=title
    album.c_name=c_name
    db.session.add(album)
    db.session.commit()
    return redirect(url_for('view_albums'))




@app.route('/album/<int:id>/delete')
def delete_album(id):
    album=Album.query.get(id)
    return render_template('deletealbum.html', user=User.query.get(session['user_id']), album=Album.query.all())



@app.route('/album/<int:id>/delete', methods=['POST'])
def delete_album_post(id):
    album=Album.query.get(id)
    if not album:
        flash('Album Not Found')
        return redirect(url_for('view_albums'))
    db.session.delete(album)
    db.session.commit()
    flash('Album Deleted Successfully')
    return redirect(url_for('view_albums'))

    




# .............................playlist. route.........................................





@app.route('/create_playlist', methods=['GET', 'POST'])
def create_playlist():
    if request.method == 'POST':
        name = request.form['name']
        playlist = Playlist(name=name, user_id=session['user_id'])
        db.session.add(playlist)
        db.session.commit()
        flash('Playlist created successfully', 'success')
        return redirect(url_for('playlists'))
    song=Song.query.all()
    return render_template('create_playlist.html' , songs=song)




@app.route('/playlists')
def playlists():
    playlist=Playlist.query.all()
    user=User.query.get(session['user_id'])
    return render_template('view_playlists.html', playlists=playlist , user=user )




@app.route('/playlist/<int:playlist_id>')
def view_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    if playlist:
        songs = Song.query.all()
        return render_template('view_playlist.html', playlist=playlist, songs=songs)
    else:
        return 'Playlist not found'



@app.route('/playlist/<int:id>/edit')
def edit_playlist(id):
    playlist=Playlist.query.get(id)
    user=User.query.get(session['user_id'])
    if user.creator:
        return render_template('editplaylist.html', user=User.query.get(session['user_id']), playlists=Playlist.query.all())
    flash('You Not Have Right Permission to Edit Playlist')
    return redirect(url_for('playlists'))




@app.route('/playlist/<int:id>/edit', methods=['POST'])
def edit_playlist_post(id):
    playlist=Playlist.query.get(id)
    title=request.form.get('title')
    playlist.name=title
    db.session.add(playlist)
    db.session.commit()
    return redirect(url_for('playlists'))



@app.route('/playlist/<int:id>/delete')
def delete_playlist(id):
    playlist=Playlist.query.get(id)
    user=User.query.get(session['user_id'])
    if user.creator:
        return render_template('deleteplaylist.html', user=User.query.get(session['user_id']), playlists=Playlist.query.all())
    flash('Permission Denied')
    return redirect(url_for('playlists'))




@app.route('/playlist/<int:id>/delete', methods=['POST'])
def delete_playlist_post(id):
    playlist=Playlist.query.get(id)
    if not playlist:
        flash('Playlist Not Found')
        return redirect(url_for('playlists'))
    db.session.delete(playlist)
    db.session.commit()
    flash('Playlist Deleted Successfully')
    return redirect(url_for('playlists'))





# ....................search functionality..................................................





@app.route('/search' , methods=['POST'])
def search():
    input=request.form.get('search')
    input_type=request.form.get('input_type', 'song')

    if input_type == 'song':
        songs=Song.query.filter(Song.title.ilike(f'%{input}%')).all()
        return render_template('input_result.html', input=input , input_type=input_type, songs=songs)
    
    if input_type == 'album':
        albums=Album.query.filter(Album.title.ilike(f'%{input}%')).all()
        return render_template('input_result.html', input=input , input_type=input_type, albums=albums)
    
    if input_type == 'genre':
        genres=Song.query.filter(Song.genre.ilike(f'%{input}%')).all()
        return render_template('input_result.html', input=input , input_type=input_type, genres=genres)
    
    
    if input_type == 'playlist':
        playlists=Playlist.query.filter(Playlist.name.ilike(f'%{input}%')).all()
        return render_template('input_result.html', input=input , input_type=input_type, playlists=playlists)
    
    return redirect(url_for('play'))




if __name__ == "__main__":
    app.run(debug=True)


