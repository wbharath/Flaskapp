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
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from logging.handlers import RotatingFileHandler
from werkzeug.exceptions import HTTPException  # Import HTTPException for error handling
from markupsafe import Markup
import re
from sqlalchemy import or_

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Initialize Flask app
app = Flask(__name__)

# Flask app configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'your_secret_key')

# Session management configurations for server-side session security
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_SQLALCHEMY'] = db
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

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
login_manager.login_view = 'auth'  # Set to 'auth' for combined login/register route

# Set up Flask-Limiter for rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# Import database models after initializing db
with app.app_context():
    from models import Login, Artist, Picture, Value

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Login.query.get(int(user_id))

# Route to redirect to auth page
@app.route('/')
def home_redirect():
    return redirect(url_for('auth'))



# Combined Login and Registration Route
@app.route('/auth', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def auth():
    login_form = LoginForm()
    register_form = RegistrationForm()

    if request.method == 'POST':
        # Handle Registration Form Submission
        if 'register' in request.form and register_form.validate_on_submit():
            if register_form.password.data != register_form.confirm_password.data:
                flash('Passwords do not match. Please try again.', 'danger')
            else:
                hashed_password = generate_password_hash(register_form.password.data)
                user = Login(
                    username=register_form.username.data,
                    email=register_form.email.data,
                    password_hash=hashed_password,
                    role='User'  # Set role appropriately
                )
                db.session.add(user)
                db.session.commit()
                flash('Your account has been created!', 'success')
                return redirect(url_for('auth'))  # Redirect to auth page to show login form

        # Handle Login Form Submission
        elif 'login' in request.form and login_form.validate_on_submit():
            user = Login.query.filter_by(email=login_form.email.data).first()
            ip_address = request.remote_addr
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if user is None:
                app.logger.warning(f"Failed login attempt for non-existent email: {login_form.email.data} from IP: {ip_address} at {timestamp}")
                flash("Email doesn't exist, please register", 'warning')
            elif user and check_password_hash(user.password_hash, login_form.password.data):
                login_user(user, remember=login_form.remember.data, duration=timedelta(hours=1))
                app.logger.info(f"User {user.email} logged in successfully from IP: {ip_address} at {timestamp}")
                flash('Login successful!', 'success')
                session['user_id'] = user.id
                session['username'] = user.username

                next_page = request.args.get('next')
                if user.role.strip().lower() == 'webmaster':
                    return redirect(next_page) if next_page else redirect(url_for('manage_art'))
                else:
                    return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                app.logger.warning(f"Failed login attempt for user: {login_form.email.data} from IP: {ip_address} at {timestamp}")
                flash('Login failed. Check your email and/or password', 'danger')

    return render_template('auth.html', login_form=login_form, register_form=register_form)

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
            app.logger.error(f'Error sending email: {e}')
            flash('An error occurred while sending your message. Please try again.', 'danger')
            return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

# Route for user logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth'))


@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template("429.html", message="Too many requests. Please try again later."), 429

@app.route('/manage_art', methods=['GET', 'POST'])
@login_required
def manage_art():
    print(f"Current user ID: {current_user.id}")
    print(f"Current user role: {current_user.role}")

    if current_user.role.strip().lower() != 'webmaster':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))

    form = ManageArtForm()

    if form.validate_on_submit():
        try:
            # Sanitize and process artist fields
            artist_name = bleach.clean(form.artist_name.data, tags=[], strip=True)
            artist_birth = form.artist_birth.data
            artist_death = form.artist_death.data if form.is_deceased.data else None
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

            # Sanitize and process value fields
            nscc_location = bleach.clean(form.nscc_location.data, tags=[], strip=True)
            initial_appraisal = form.initial_appraisal.data
            new_appraisal = form.new_appraisal.data
            purchase_price = form.purchase_price.data
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

            # Handle picture upload
            if form.picture.data:
                filename = secure_filename(form.picture.data.filename)
                picture_path = os.path.join('static/images', filename)
                form.picture.data.save(picture_path)

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
        except Exception as e:
            db.session.rollback()
            flash('An unexpected error occurred. Please try again.', 'danger')
            print(f"Error: {e}")
        
        return redirect(url_for('manage_art'))
    elif form.errors:
        flash('There was an error in the form. Please check the fields below.', 'danger')
        print(form.errors)

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
                flash("Your profile has been updated successfully!", "success")
            else:
                flash("Current password is incorrect.", "danger")
        else:
            flash("Please enter your current password to update your profile.", "warning")

    return render_template('profile.html', form=form)

@app.before_request
def refresh_user():
    if current_user.is_authenticated:
        db.session.refresh(current_user)

# Configure logging
if not app.debug:  # Only log in production mode
    file_handler = RotatingFileHandler('flaskapp.log', maxBytes=10240, backupCount=10, delay=True)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("Flask Art Management Application startup")

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    app.logger.error(f"An error occurred: {e}")
    return "An internal error occurred", 500

# Route to display homepage with artwork data and handle search queries
@app.route('/home', methods=['GET'])
@login_required
def index():
    search_query = request.args.get('search', '').strip()
    filter_artist = request.args.get('filter_artist')
    filter_title = request.args.get('filter_title')

    filters = []
    if filter_artist:
        filters.append('artist')
    if filter_title:
        filters.append('title')

    query_filters = []

    if search_query:
        if filter_artist and filter_title:
            query_filters.append(
                or_(
                    Picture.title.ilike(f'%{search_query}%'),
                    Artist.artist_name.ilike(f'%{search_query}%')
                )
            )
        elif filter_artist:
            query_filters.append(Artist.artist_name.ilike(f'%{search_query}%'))
        elif filter_title:
            query_filters.append(Picture.title.ilike(f'%{search_query}%'))
        else:
            query_filters.append(
                or_(
                    Picture.title.ilike(f'%{search_query}%'),
                    Artist.artist_name.ilike(f'%{search_query}%'),
                    Value.nscc_location.ilike(f'%{search_query}%'),
                    Value.provenance.ilike(f'%{search_query}%')
                )
            )

    if query_filters:
        pictures = Picture.query.join(Artist).join(Value).filter(*query_filters).all()
    else:
        pictures = Picture.query.join(Artist).join(Value).all()

    return render_template('index.html', pictures=pictures, search_query=search_query, filters=filters)

@app.template_filter('highlight')
def highlight(text, search):
    if not search:
        return text
    # Escape special characters in the search query
    escaped_search = re.escape(search)
    pattern = re.compile(escaped_search, re.IGNORECASE)
    highlighted = pattern.sub(lambda match: Markup(f"<mark>{match.group(0)}</mark>"), text)
    return highlighted

if __name__ == '__main__':
    app.run(debug=True)
