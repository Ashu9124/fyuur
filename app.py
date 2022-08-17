#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
# work inspired from : https://github.com/justicemartinez/fyyurapp/blob/main/Fyyur%20Project/app.py
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
from model import Venue, Artist, Show
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)


app.config ['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost:5432/todoapp'
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # completed: replace with real venues data
  areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
  # print(areas)
  data = []
  for area in areas:
    results = db.session.query(Venue.name,Venue.id).filter(Venue.city == area.city,Venue.state == area.state).all()
    venue_data = [i for i in results]
    data.append({
        'city': area.city,
        'state': area.state,
        'venues': venue_data
      })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['GET','POST'])
def search_venues():
  # completed: implement search on artists with partial string search. Ensure it is case-insensitive.
  search_term = request.form.get('search_term', '')
  venue_details = db.session.query(Venue).filter(Venue.name.ilike(f"%{search_term}%")).all()
  data = {
    "count":len(venue_details),
    "data": venue_details
  }
  return render_template('pages/search_venues.html', results=data,
                         search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # completed: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter(Venue.id == venue_id).first()

  upcoming_shows = []
  past_shows = []

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": [venue.genres],
    "city": venue.city,
    "state": venue.state,
    "address": venue.address,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
  }

  upcoming_show = db.session.query(Show,Artist).filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).join(Artist, Show.artist_id == Artist.id)

  for newshow,artist in upcoming_show:
    upcoming_shows.append({
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': str(newshow.start_time)
    })
  data['upcoming_shows'] = upcoming_shows
  data['upcoming_shows_count'] = len(upcoming_shows)
  past_show = db.session.query(Show, Artist).filter(Show.venue_id == venue_id).filter(
    Show.start_time < datetime.now()).join(Artist, Show.artist_id == Artist.id)
  for oldshow,artist_past in past_show:
    past_shows.append({
      'artist_id': artist_past.id,
      'artist_name': artist_past.name,
      'image_link': artist_past.image_link,
      'start_time': str(oldshow.start_time)
    })
  data['past_shows'] = past_shows
  data['past_shows_count'] = len(past_shows)


  return render_template('pages/show_venue.html', venue=data)



#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['GET','POST'])
def create_venue_submission():
  # complt: insert form data as a new Venue record in the db, instead
  # compl: modify data to be the data object returned from db insertion
  try:
    venue = Venue(
      name=request.form['name'],
      city=request.form['city'],
      state=request.form['state'],
      address=request.form['address'],
      phone=request.form['phone'],
      genres=request.form.getlist('genres'),


      seeking_talent=json.loads(request.form['seeking_talent']),
      seeking_description=request.form['seeking_description']
    )
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    print(e)
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter(Venue.id == venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  artist_search = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = {
    "count": len(artist_search),
    "data": artist_search
  }
  return render_template('pages/search_artists.html', results=data, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter(Artist.id == artist_id).first()
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": [artist.genres],
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link}


  past_show = db.session.query(Show,Venue).filter(Show.artist_id == artist_id).filter(
    Show.start_time < datetime.now()).join(Venue, Show.venue_id == Venue.id)
  upcoming_show = db.session.query(Show,Venue).filter(Show.artist_id == artist_id).filter(
    Show.start_time > datetime.now()).join(Venue, Show.venue_id == Venue.id)

  past_shows = []

  for newshow,venue in upcoming_show:
    upcoming_shows.append({
      'venue_id': venue.id,
      'venue_name': venue.name,
      'image_link': venue.image_link,
      'start_time': str(newshow.start_time)
    })

  for oldshow, venue in past_show:
    past_shows.append({
      'venue_id': venue.id,
      'venue_name': venue.name,
      'image_link': venue.image_link,
      'start_time': str(oldshow.start_time)
    })




    data["past_shows"] = past_shows
    date["upcoming_shows"]= upcoming_shows
    data["past_shows_count"]= len(past_show)
    data["upcoming_shows_count"]= len(upcoming_show)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter(Artist.id == artist_id).first()
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # completed: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    artist = Artist(
      name=request.form['name'],
      city=request.form['city'],
      state=request.form['state'],
      phone=request.form['phone'],
      genres=request.form.getlist('genres'),
      image_link=request.form['image_link'],
      facebook_link=request.form['facebook_link'],
      seeking_venue=json.loads(request.form['seeking_venue'].lower()),
      website=request.form['website_link'],
      seeking_description=request.form['seeking_description']
    )
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    print(e)
    flash('An error occurred' + str(e)+'. Artist ' + request.form['name'] + ' could not be listed')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  show_details = Show.query.join(Artist, Artist.id == Show.artist_id).join(Venue, Venue.id == Show.venue_id).all()

  data = []
  for show in show_details:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    show = Show(
      artist_id=request.form['artist_id'],
      venue_id=request.form['venue_id'],
      start_time=request.form['start_time']
    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except Exception as e:
    print(e)
    flash('An error occurred'+str(e)+'. Show could not be listed')
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
