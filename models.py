from extensions import db  # Import db from extensions.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Login(UserMixin, db.Model):
    __tablename__ = 'login'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='User')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String(255), nullable=False)
    artist_birth = db.Column(db.Date, nullable=False)
    artist_death = db.Column(db.Date, nullable=True)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(50), nullable=True)

    # Relationships
    pictures = db.relationship('Picture', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist {self.artist_name}>'

class Value(db.Model):
    __tablename__ = 'value'

    id = db.Column(db.Integer, primary_key=True)
    nscc_location = db.Column(db.String(255), nullable=False)
    initial_appraisal = db.Column(db.Numeric(10, 2), nullable=False)
    new_appraisal = db.Column(db.Numeric(10, 2), nullable=True)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    relevant_contact_info = db.Column(db.String(255), nullable=True)
    provenance = db.Column(db.Text, nullable=True)

    # Relationships
    pictures = db.relationship('Picture', backref='value', lazy=True)

    def __repr__(self):
        return f'<Value {self.id}>'

class Picture(db.Model):
    __tablename__ = 'picture'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    value_id = db.Column(db.Integer, db.ForeignKey('value.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_path = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Picture {self.title}>'

# Session model for server-side session storage
class Session(db.Model):
    __tablename__ = 'session'
    session_id = db.Column(db.String(255), primary_key=True)
    data = db.Column(db.LargeBinary)
    expiry = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Session {self.session_id}>'