from flask_sqlalchemy import SQLAlchemy
import datetime
db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    address = db.Column(db.String)
    phone = db.Column(db.String)
    image_link = db.Column(db.String)
    facebook_link = db.Column(db.String)
    genres = db.Column(db.String)# changed to array
    website = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'

    # completed: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    phone = db.Column(db.String)
    genres = db.Column(db.String)#changed to array
    image_link = db.Column(db.String)
    facebook_link = db.Column(db.String)
    website = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean,default = False)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'
    # completed: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.



class Show(db.Model):
  __tablename__ = 'Shows'

  id = db.Column(db.Integer, primary_key=True)
  artist_id= db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id= db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.DateTime,nullable=False)

  def __repr__(self):
    return f'<Show {self.id} {self.artist_id} {self.venue_id} {self.start_time}>'
