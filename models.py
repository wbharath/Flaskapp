from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db  # Import db from extensions.py

class Login(UserMixin, db.Model):
    __tablename__ = 'login'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(64), nullable=False, default='User')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String(255), nullable=False)
    artist_birth = db.Column(db.Date)
    artist_death = db.Column(db.Date)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))

    # Relationships
    pictures = db.relationship('Picture', backref='artist', lazy=True)

class Picture(db.Model):
    __tablename__ = 'picture'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    value_id = db.Column(db.Integer, db.ForeignKey('value.id'))
    created_at = db.Column(db.Date)

class Value(db.Model):
    __tablename__ = 'value'

    id = db.Column(db.Integer, primary_key=True)
    nscc_location = db.Column(db.String(255))
    initial_appraisal = db.Column(db.Numeric(10, 2))
    new_appraisal = db.Column(db.Numeric(10, 2))
    purchase_price = db.Column(db.Numeric(10, 2))
    relevant_contact_info = db.Column(db.String(255))
    provenance = db.Column(db.Text)

    # Relationships
    pictures = db.relationship('Picture', backref='value', lazy=True)
