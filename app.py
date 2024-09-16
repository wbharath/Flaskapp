from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, ContactForm
from flask_mail import Mail, Message


import os
app = Flask(__name__)

# Flask app configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Mokshagna%40123@localhost/data1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set the secret key from environment variable
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')

# Initialize the database and migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'bharadwajdurgasai@gmail.com'
app.config['MAIL_PASSWORD'] = 'yubj nugq ardo otkp'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Define the Item model
class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))

@app.route('/')
def home_redirect():
    return redirect(url_for('register'))

@app.route('/home')
def index():
    items = Item.query.all()  # Fetch all items from the database
    return render_template('index.html', items=items)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your email and/or password', 'danger')
    return render_template('login.html', form=form)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data
        
        msg = Message('Contact Form Message', sender=email, recipients=['your_email@gmail.com'])
        msg.body = f"Message from {name} ({email}):\n\n{message}"
        mail.send(msg)
        flash('Message sent successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('contact.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
