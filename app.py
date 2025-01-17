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
from PIL import Image
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



@app.route('/auth', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def auth():
    login_form = LoginForm()
    register_form = RegistrationForm()
    if request.method == 'POST':
        # ---- Handle Registration Form Submission ----
        if 'register' in request.form:
            # If the form validates, that includes matching passwords via EqualTo('password').
            if register_form.validate_on_submit():
                #hashing the password for secure storage
                hashed_password = generate_password_hash(register_form.password.data)
                #creating a new user object
                user = Login(
                    username=register_form.username.data,
                    email=register_form.email.data,
                    password_hash=hashed_password,
                    role='User'
                ) #here default role is assigned to the user
                #adding the user to the DB
                db.session.add(user)
                db.session.commit()
                #success message to user
                flash('Your account has been created!', 'success')
                return redirect(url_for('auth'))  # Redirect to show login form
            else:
                # WTForms caught some error (passwords mismatch, invalid email, etc.)
                app.logger.warning("Registration form validation failed.")
                # re-rendering the auth-page with errors
                return render_template('auth.html',
                                       login_form=login_form,
                                       register_form=register_form)

        # ---- Handle Login Form Submission ----
        elif 'login' in request.form and login_form.validate_on_submit():
            # Querying the database for the user with the provided email
            user = Login.query.filter_by(email=login_form.email.data).first()
            #getting the client's IP address
            ip_address = request.remote_addr
            #current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # If no user is found with the provided email
            if user is None:
                # Logging a warning for a failed login attempt
                app.logger.warning(
                    f"Failed login attempt for non-existent email: {login_form.email.data} "
                    f"from IP: {ip_address} at {timestamp}"
                )
                #flash the message to the user
                flash("Email doesn't exist, please register", 'warning')

            #if user is there checks password match or not with db
            elif user and check_password_hash(user.password_hash, login_form.password.data):
                # Log the user in with a session
                login_user(user, remember=login_form.remember.data, duration=timedelta(hours=1))
                # Log successful login attempt
                app.logger.info(
                    f"User {user.email} logged in successfully from IP: {ip_address} at {timestamp}"
                )
                # Flash success message
                flash('Login successful!', 'success')
                # Storing user information in the session table for extra security
                session['user_id'] = user.id
                session['username'] = user.username

                #redirecting to the page based on the role
                next_page = request.args.get('next')
                #if user role is webmaster he can view manage_art_page
                if user.role.strip().lower() == 'webmaster':
                    return redirect(next_page) if next_page else redirect(url_for('manage_art'))
                #if user role is not webmaster he will be redirected to home-page
                else:
                    return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                # logging a warning for failed login due to incorrect password
                app.logger.warning(
                    f"Failed login attempt for user: {login_form.email.data} "
                    f"from IP: {ip_address} at {timestamp}"
                )
                 # flash an error message for invalid credentials
                flash('Login failed. Check your email and/or password', 'danger')

    # render the auth page for GET requests or when no matching POST action occurs
    return render_template('auth.html', login_form=login_form, register_form=register_form)



# Route for contact form
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    #initializing the form
    form = ContactForm()
    # Checking if the form was submitted and is valid
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data
        status = form.status.data
        campus = form.campus.data

        # Creating the email message object
        msg = Message('Contact Form Message', sender=email, recipients=['bharadwajdurgasai@gmail.com'])
        #body of email
        msg.body = f'''
        
        Message from {name} ({email}):

        Status: {status}
        Campus: {campus}
        Message: {message}
        '''
        try:
            #sending mail with form details
            mail.send(msg)
            # flash success message if email is sent
            flash('Message sent successfully!', 'success')
            # redirect the user to the index page after success
            return redirect(url_for('index'))
        except Exception as e:
            #logging the error in case of an exception
            app.logger.error(f'Error sending email: {e}')
            # flash an error message to notify the user
            flash('An error occurred while sending your message. Please try again.', 'danger')
            # redirect the user back to the contact page
            return redirect(url_for('contact'))
    # render the contact page with the contact form for GET requests or invalid submissions
    return render_template('contact.html', form=form)

# Route for user logout
@app.route('/logout')
@login_required
def logout():
    #logouts the user (Flask login handles this(makes current user to AnnonymousUserMixin))
    logout_user()
    #clears the session
    session.clear()
    #flash the message to user
    flash('You have been logged out.', 'info')
    #finally redirect them to home
    return redirect(url_for('auth'))


@app.errorhandler(429)
def ratelimit_handler(e):
    # render a custom HTML template for rate limit errors
    # Passing a message to the template to inform the user about the error
    return render_template("429.html", message="Too many requests. Please try again later."), 429


# route for managing art (accessible only to webmasters)
@app.route('/manage_art', methods=['GET', 'POST'])
@login_required # Ensures the user is logged in to access this page
def manage_art():

    # print(f"Current user ID: {current_user.id}")
    # print(f"Current user role: {current_user.role}")

    # restricting access to users except with "webmaster" role
    if current_user.role.strip().lower() != 'webmaster':
        flash('You do not have permission to access this page.', 'danger')
        # redirect unauthorized users to the home page
        return redirect(url_for('index'))

    # initializing the art management form
    form = ManageArtForm()

    # handling form submission
    if form.validate_on_submit():
        try:
            # process and sanitize artist fields
            artist_name = bleach.clean(form.artist_name.data, tags=[], strip=True)
            artist_birth = form.artist_birth.data
            artist_death = form.artist_death.data if form.is_deceased.data else None
            email = bleach.clean(form.email.data, tags=[], strip=True)
            phone = bleach.clean(form.phone.data, tags=[], strip=True)

            # creating and save the Artist object
            artist = Artist(
                artist_name=artist_name,
                artist_birth=artist_birth,
                artist_death=artist_death,
                email=email,
                phone=phone
            )
            #adding the artist object to the db
            db.session.add(artist)
            db.session.commit()

            # process and sanitize value fields
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
            #adding to Db
            db.session.add(value)
            db.session.commit()

            # Handle picture upload
            file = request.files.get('file') # retrieving uploaded file
            if file and allowed_file(file.filename): # validating file type
                if not file_size(file):# checking file size (5 MB limit)
                    flash('File size exceeds 5 MB limit.', 'danger')
                    return redirect(url_for('manage_art'))

                # Securing the filename and determine the file path
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                 # Save and verify the uploaded file as a valid image
                try:
                    file.save(file_path)
                    with Image.open(file_path) as img:
                        img.verify()  # Ensure it's a valid image
                except Exception:
                    os.remove(file_path)# Remove invalid files
                    flash('Uploaded file is not a valid image.', 'danger')
                    return redirect(url_for('manage_art'))

                # sanitize and save the picture details
                title = bleach.clean(form.title.data, tags=[], strip=True)

                picture = Picture(
                    title=title,
                    artist_id=artist.id,
                    value_id=value.id,
                    created_at=datetime.utcnow(),
                    image_path=f'images/{filename}'# storing image path relative to the app
                )
                db.session.add(picture)
                db.session.commit()

                # show success message if all operations succeed
                flash('Art has been successfully uploaded!', 'success')
            else:
                flash('Invalid file type. Only JPG and PNG are allowed.', 'danger')
        except Exception as e:# handling unexpected errors
            db.session.rollback()  # roll back the transaction to prevent partial saves
            flash('An unexpected error occurred. Please try again.', 'danger')
            # print(f"Error: {e}")

        # redirect to the same page after handling the form
        return redirect(url_for('manage_art'))
    elif form.errors:# handle form validation errors
        flash('There was an error in the form. Please check the fields below.', 'danger')
        # print(form.errors)

    # render the art management page with the form
    return render_template('art.html', form=form)


# route to update user profile
@app.route('/profile', methods=['GET', 'POST'])
@login_required # snsures the user is logged in to access this page
def profile():
    # initializing the profile update form
    form = UpdateProfileForm()

    # pre-fills the form fields with the current user's information on GET requests
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

     # handles form submission for updating profile information
    if form.validate_on_submit():
         # check if the user provided their current password
        if form.current_password.data:
            # verify the current password against the stored password hash
            if check_password_hash(current_user.password_hash, form.current_password.data):
                # update the user's username and email
                current_user.username = form.username.data
                current_user.email = form.email.data

                # update the password if a new one is provided
                if form.password.data:
                    current_user.password_hash = generate_password_hash(form.password.data)
                # commit the changes to the database
                db.session.commit()
                #flash user 
                flash("Your profile has been updated successfully!", "success")
            else:
                #flash error
                flash("Current password is incorrect.", "danger")
        else:
            #flash error if current password provided is wrong
            flash("Please enter your current password to update your profile.", "warning")
    #render profile page page with update form
    return render_template('profile.html', form=form)

 #hook to refresh the current user's data before every request
@app.before_request
def refresh_user():
    # checks if the user is authenticated
    if current_user.is_authenticated:
        # refresh the user's data from the database
        db.session.refresh(current_user)

# Configure logging
if not app.debug:  # Only log in production mode
    file_handler = RotatingFileHandler('flaskapp.log', maxBytes=10240, backupCount=10, delay=True)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("Flask Art Management Application startup")

# global error handler for unexpected exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    # if the exception is an HTTPException, Flask will handle it
    if isinstance(e, HTTPException):
        return e
    # logging the error for debugging and monitoring purposes
    app.logger.error(f"An error occurred: {e}")

    # return a generic error message and a 500 Internal Server Error status code
    return "An internal error occurred", 500

# route to display homepage with artwork data and handle search queries
@app.route('/home', methods=['GET'])
@login_required
def index():
    # retrieving query parameters from the URL(search)
    search_query = request.args.get('search', '').strip() # search query, defaults to an empty string
    filter_artist = request.args.get('filter_artist') # check if artist filter is selected
    filter_title = request.args.get('filter_title') # check if title filter is selected

    # list to store active filters for display purposes
    filters = []
    if filter_artist:
        filters.append('artist')# add 'artist' filter if selected
    if filter_title:
        filters.append('title')# add 'title' filter if selected

    # initialize a list for SQLAlchemy query filters
    query_filters = []

    # builds the query filters based on the search query and selected filters
    if search_query:
        # if both artist and title filters are selected
        if filter_artist and filter_title:
            query_filters.append(
                or_(
                    Picture.title.ilike(f'%{search_query}%'),
                    Artist.artist_name.ilike(f'%{search_query}%')
                )
            )
        # if only artist filter is selected
        elif filter_artist:
            query_filters.append(Artist.artist_name.ilike(f'%{search_query}%'))#search in artist
        # if only title filter is selected
        elif filter_title:
            query_filters.append(Picture.title.ilike(f'%{search_query}%'))#search in title

         # If no specific filter is selected, search across multiple fields
        else:
            query_filters.append(
                or_(
                    Picture.title.ilike(f'%{search_query}%'),# search in Picture titles
                    Artist.artist_name.ilike(f'%{search_query}%'),#search in artist name
                    Value.nscc_location.ilike(f'%{search_query}%'),#search in location
                    Value.provenance.ilike(f'%{search_query}%')#search in province
                )
            )
    # execute the query based on the constructed filters
    if query_filters:
        # apply filters to the query and retrieve matching results
        pictures = Picture.query.join(Artist).join(Value).filter(*query_filters).all()
    else:
        # retrieve all records if no filters are applied
        pictures = Picture.query.join(Artist).join(Value).all()

    # render the home page with the results and search/filter data
    return render_template('index.html', pictures=pictures, search_query=search_query, filters=filters)

@app.template_filter('highlight')
def highlight(text, search):
    if not search:
        return text
    # Escape special characters in the search query
    escaped_search = re.escape(search)
    pattern = re.compile(escaped_search, re.IGNORECASE)
    #highlights the matched result
    highlighted = pattern.sub(lambda match: Markup(f"<mark>{match.group(0)}</mark>"), text)
    return highlighted

# Configuration for upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Check if file type is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Validate file size
def file_size(file):
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)  # Reset file pointer
    return size <= MAX_FILE_SIZE


if __name__ == '__main__':
    app.run(debug=True)
