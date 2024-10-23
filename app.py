from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_session import Session
from flask_migrate import Migrate
from extensions import db  # Import db from extensions.py
from forms import RegistrationForm, LoginForm, ContactForm, UpdateProfileForm, ManageArtForm
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import bleach
from werkzeug.utils import secure_filename


# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Flask app configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Mokshagna%40123@localhost/data1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'your_secret_key')

# Session management configurations for server-side session security
app.config['SESSION_TYPE'] = 'sqlalchemy'  # Use server-side session management
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Sessions expire after 30 minutes of inactivity
app.config['SESSION_USE_SIGNER'] = True  # Sign the session cookie for extra security
app.config['SESSION_SQLALCHEMY'] = db  # Link SQLAlchemy session to our database
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript from accessing the session cookie
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True when running over HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Prevent CSRF attacks by limiting cross-site requests

# Initialize database and migration
db.init_app(app)
migrate = Migrate(app, db)

# Initialize Flask-Session
Session(app)

# CSRF Protection
csrf = CSRFProtect(app)
csrf.init_app(app)

# Mail server configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') 
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False') == 'True'

# Initialize Flask-Mail
mail = Mail(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import database models after initializing db
with app.app_context():
    from models import Login, Artist, Picture, Value  # Ensure models are imported after db is initialized

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    user = Login.query.get(int(user_id))
    return user

# Route to redirect to registration
@app.route('/')
def home_redirect():
    return redirect(url_for('register'))

# Route to display homepage with artwork data
@app.route('/home')
@login_required
def index():
    pictures = Picture.query.join(Artist).join(Value).all()
    return render_template('index.html', pictures=pictures)

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        # Set the role to 'Webmaster' for testing purposes
        user = Login(username=form.username.data, email=form.email.data, password_hash=hashed_password, role='Webmaster')
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Login.query.filter_by(email=form.email.data).first()
        
        if user is None:
            flash("Email doesn't exist, please register", 'warning')
        elif user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data, duration=timedelta(hours=1))  # Secure session duration
            flash('Login successful!', 'success')

            # Store user information in the session (handled server-side via SQL)
            session['user_id'] = user.id
            session['username'] = user.username

            next_page = request.args.get('next')
            if user.role.strip().lower() == 'webmaster':
                return redirect(next_page) if next_page else redirect(url_for('manage_art'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login failed. Check your email and/or password', 'danger')

    return render_template('login.html', form=form)

# Route for contact form
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data
        status = form.status.data
        campus = form.campus.data

        msg = Message('Contact Form Message', sender=email, recipients=['bharadwajdurgasai@gmail.com'])
        msg.body = f'''
        Message from {name} ({email}):

        Status: {status}
        Campus: {campus}
        Message: {message}
        '''
        try:
            mail.send(msg)
            flash('Message sent successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            print(f'Error sending email: {e}')
            flash('An error occurred while sending your message. Please try again.', 'danger')
            return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

# Route for user logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # Clear all session data
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))



@app.route('/manage_art', methods=['GET', 'POST'])
@login_required
def manage_art():
    print(f"Current user ID: {current_user.id}")
    print(f"Current user role: {current_user.role}")
    
    if current_user.role.strip().lower() != 'webmaster':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))

    form = ManageArtForm()

    # Check if the form is submitted and valid
    if form.validate_on_submit():
        # Sanitize artist fields (excluding date fields)
        artist_name = bleach.clean(form.artist_name.data, tags=[], strip=True)
        artist_birth = form.artist_birth.data  # Do not sanitize date fields
        artist_death = form.artist_death.data if form.is_deceased.data else None  # Do not sanitize date fields
        email = bleach.clean(form.email.data, tags=[], strip=True)
        phone = bleach.clean(form.phone.data, tags=[], strip=True)

        artist = Artist(
            artist_name=artist_name,
            artist_birth=artist_birth,
            artist_death=artist_death,
            email=email,
            phone=phone
        )
        db.session.add(artist)
        db.session.commit()

        # Do not sanitize decimal fields, just store them directly
        nscc_location = bleach.clean(form.nscc_location.data, tags=[], strip=True)
        initial_appraisal = form.initial_appraisal.data  # Do not sanitize decimal fields
        new_appraisal = form.new_appraisal.data  # Do not sanitize decimal fields
        purchase_price = form.purchase_price.data  # Do not sanitize decimal fields
        relevant_contact_info = bleach.clean(form.relevant_contact_info.data, tags=[], strip=True)
        provenance = bleach.clean(form.provenance.data, tags=[], strip=True)

        value = Value(
            nscc_location=nscc_location,
            initial_appraisal=initial_appraisal,
            new_appraisal=new_appraisal,
            purchase_price=purchase_price,
            relevant_contact_info=relevant_contact_info,
            provenance=provenance
        )
        db.session.add(value)
        db.session.commit()

        # Handle picture upload and picture data
        if form.picture.data:
            filename = secure_filename(form.picture.data.filename)
            picture_path = os.path.join('static/images', filename)
            form.picture.data.save(picture_path)

            # Sanitize picture title
            title = bleach.clean(form.title.data, tags=[], strip=True)

            picture = Picture(
                title=title,
                artist_id=artist.id,
                value_id=value.id,
                created_at=datetime.utcnow(),
                image_path=f'images/{filename}'
            )
            db.session.add(picture)
            db.session.commit()

            flash('Art has been successfully uploaded!', 'success')
        else:
            flash('Please upload an image.', 'danger')

        return redirect(url_for('manage_art'))

    else:
        # If form validation fails, print the errors and show a flash message
        print(form.errors)  # Log form errors to console for debugging
        flash('There was an error in the form. Please check the fields below.', 'danger')

    return render_template('art.html', form=form)

# Route to update user profile
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()

    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    if form.validate_on_submit():
        if form.current_password.data:
            if check_password_hash(current_user.password_hash, form.current_password.data):
                current_user.username = form.username.data
                current_user.email = form.email.data
                if form.password.data:
                    current_user.password_hash = generate_password_hash(form.password.data)
                db.session.commit()

                # Set up the toast message
                toast_title = "Success"
                toast_message = "Your profile has been updated successfully!"
            else:
                toast_title = "Error"
                toast_message = "Current password is incorrect."
        else:
            toast_title = "Warning"
            toast_message = "Please enter your current password to update your profile."

        return render_template('profile.html', form=form, toast_title=toast_title, toast_message=toast_message)

    return render_template('profile.html', form=form, toast_title="", toast_message="")

@app.before_request
def refresh_user():
    if current_user.is_authenticated:
        db.session.refresh(current_user)

if __name__ == '__main__':
    app.run(debug=True)
