from flask import Flask, render_template, redirect, url_for, flash, request
from flask_migrate import Migrate
from forms import RegistrationForm, LoginForm, ContactForm
from flask_mail import Mail, Message
from forms import ManageArtForm, MinimalForm
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash  # Add this line
import os
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename
from datetime import datetime


load_dotenv()

from extensions import db  # Import db from extensions.py

app = Flask(__name__)

# Flask app configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Mokshagna%40123@localhost/data1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')

# Initialize the database and migration
db.init_app(app)  # Initialize db with app
migrate = Migrate(app, db)

# Import models after initializing db
with app.app_context():
    from models import Login, Artist, Picture, Value  # Import models

# Flask app configuration using environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail server configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL') == 'True'

mail = Mail(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User loader callback
@login_manager.user_loader
def load_user(user_id):
    return Login.query.get(int(user_id))

@app.route('/')
def home_redirect():
    return redirect(url_for('register'))

@app.route('/home')
def index():
    # Assuming you have an Item model
    # items = Item.query.all()  # Uncomment if Item model exists
    return render_template('index.html')  # , items=items)



@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = Login(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            role=form.role.data  # Save the selected role
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect authenticated users away from the login page
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Login.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            if user.role == 'Webmaster':
                return redirect(next_page) if next_page else redirect(url_for('manage_art'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('index'))
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
        status = form.status.data  # Get the selected radio button value
        campus = form.campus.data
        
        msg = Message('Contact Form Message',
                      sender=email,
                      recipients=['your_email@example.com'])  # Replace with your email
        msg.body = f'''
        Message from {name} ({email}):
        
        Status: {status}

        Campus: {campus}
        
        Message:
        {message}
        '''
        try:
            mail.send(msg)
            flash('Message sent successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            print(f'Error sending email: {e}')
            flash('An error occurred while sending your message. Please try again.', 'error')
            return redirect(url_for('contact'))

    return render_template('contact.html', form=form)

# Add logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/manage_art', methods=['GET', 'POST'])
@login_required
def manage_art():
    print("Entered the manage_art route")  # Debugging step
    form = MinimalForm()  # Using the minimal form

    if form.validate_on_submit():
        flash('Form submitted successfully!', 'success')
        return redirect(url_for('manage_art'))

    return render_template('art.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
