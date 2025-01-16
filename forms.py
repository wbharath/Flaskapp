from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, RadioField, SelectField, DecimalField, FileField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp, ValidationError
from flask_wtf.file import FileAllowed



from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20),
        Regexp('^[a-zA-Z0-9_]*$', message="Username can only contain letters, numbers, and underscores.")
    ])
    email = StringField('Email', validators=[
    DataRequired(),
    Regexp(
        r'^[^@]+@[^@]+\.(com|org|net|edu)$',
        message="Please enter a valid email with .com, .org, .net, or .edu.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, max=20)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match.")
    ])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    status = RadioField('Are you an NSCC Employee or NSCC Student?', 
                        choices=[('NSCC Employee', 'NSCC Employee'), 
                                 ('NSCC Student', 'NSCC Student')],
                        validators=[DataRequired()])
    campus = SelectField('Select NSCC Campus', 
                         choices=[
                             ('', '-- Select a Campus --'),
                             ('Akerley Campus (Dartmouth, NS)', 'Akerley Campus (Dartmouth, NS)'),
                             ('Amherst Learning Centre (Amherst, NS)', 'Amherst Learning Centre (Amherst, NS)'),
                             ('Annapolis Valley Campus (Middleton, NS)', 'Annapolis Valley Campus (Middleton, NS)'),
                             ('Burridge Campus (Yarmouth, NS)', 'Burridge Campus (Yarmouth, NS)'),
                             ('Centre of Geographic Sciences (Lawrencetown, NS)', 'Centre of Geographic Sciences (Lawrencetown, NS)'),
                             ('Cumberland Campus (Springhill, NS)', 'Cumberland Campus (Springhill, NS)'),
                             ('Digby Learning Centre (Digby, NS)', 'Digby Learning Centre (Digby, NS)'),
                             ('eCampus (Online)', 'eCampus (Online)'),
                             ('Institute of Technology Campus (Halifax, NS)', 'Institute of Technology Campus (Halifax, NS)'),
                             ('Ivany Campus (Dartmouth, NS)', 'Ivany Campus (Dartmouth, NS)'),
                             ('Kingstec Campus (Kentville, NS)', 'Kingstec Campus (Kentville, NS)'),
                             ('Lunenburg Campus (Bridgewater, NS)', 'Lunenburg Campus (Bridgewater, NS)'),
                             ('Pictou Campus (Stellarton, NS)', 'Pictou Campus (Stellarton, NS)'),
                             ('Shelburne Campus (Shelburne, NS)', 'Shelburne Campus (Shelburne, NS)'),
                             ('Strait Area Campus (Port Hawkesbury, NS)', 'Strait Area Campus (Port Hawkesbury, NS)'),
                             ('Sydney Waterfront Campus (Sydney, NS)', 'Sydney Waterfront Campus (Sydney, NS)'),
                             ('Truro Campus (Truro, NS)', 'Truro Campus (Truro, NS)')
                         ],
                         validators=[DataRequired()])
    submit = SubmitField('Submit')

class ManageArtForm(FlaskForm):
    title = StringField('Art Title', validators=[DataRequired()])
    artist_name = StringField('Artist Name', validators=[DataRequired()])
    
    # Date fields for birth and death
    artist_birth = DateField('Artist Birth', format='%Y-%m-%d', validators=[DataRequired()])
    is_deceased = BooleanField('Deceased')  # Checkbox for deceased status
    artist_death = DateField('Artist Death', format='%Y-%m-%d', validators=[Optional()])  # Optional death date
    
    email = StringField('Artist Email', validators=[Email(message="Invalid email address")])
    
    # Phone number validation using regex
    phone = StringField('Phone Number', validators=[Regexp(r'^\+?1?\d{9,15}$', message="Enter a valid phone number. Ex: +123456789")])
    
    # SelectField for NSCC location
    nscc_location = SelectField(
        'Select NSCC Campus',
        choices=[
            ('', '-- Select a Campus --'),
            ('Akerley Campus (Dartmouth, NS)', 'Akerley Campus (Dartmouth, NS)'),
            ('Amherst Learning Centre (Amherst, NS)', 'Amherst Learning Centre (Amherst, NS)'),
            ('Annapolis Valley Campus (Middleton, NS)', 'Annapolis Valley Campus (Middleton, NS)'),
            ('Burridge Campus (Yarmouth, NS)', 'Burridge Campus (Yarmouth, NS)'),
            ('Centre of Geographic Sciences (Lawrencetown, NS)', 'Centre of Geographic Sciences (Lawrencetown, NS)'),
            ('Cumberland Campus (Springhill, NS)', 'Cumberland Campus (Springhill, NS)'),
            ('Digby Learning Centre (Digby, NS)', 'Digby Learning Centre (Digby, NS)'),
            ('eCampus (Online)', 'eCampus (Online)'),
            ('Institute of Technology Campus (Halifax, NS)', 'Institute of Technology Campus (Halifax, NS)'),
            ('Ivany Campus (Dartmouth, NS)', 'Ivany Campus (Dartmouth, NS)'),
            ('Kingstec Campus (Kentville, NS)', 'Kingstec Campus (Kentville, NS)'),
            ('Lunenburg Campus (Bridgewater, NS)', 'Lunenburg Campus (Bridgewater, NS)'),
            ('Pictou Campus (Stellarton, NS)', 'Pictou Campus (Stellarton, NS)'),
            ('Shelburne Campus (Shelburne, NS)', 'Shelburne Campus (Shelburne, NS)'),
            ('Strait Area Campus (Port Hawkesbury, NS)', 'Strait Area Campus (Port Hawkesbury, NS)'),
            ('Sydney Waterfront Campus (Sydney, NS)', 'Sydney Waterfront Campus (Sydney, NS)'),
            ('Truro Campus (Truro, NS)', 'Truro Campus (Truro, NS)')
        ],
        validators=[DataRequired(message="Please select a valid NSCC campus.")]
    )
    
    initial_appraisal = DecimalField('Initial Appraisal', validators=[DataRequired()])
    new_appraisal = DecimalField('New Appraisal', validators=[Optional()])
    purchase_price = DecimalField('Purchase Price', validators=[DataRequired()])
    relevant_contact_info = StringField('Relevant Contact Info', validators=[Optional()])
    provenance = StringField('Provenance', validators=[Optional()])
    
    #File header signature 
    picture = FileField('Art Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    
    submit = SubmitField('Submit')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    # Add the current password field to verify identity
    current_password = PasswordField('Current Password', validators=[DataRequired()])

    # Add new password fields for updating the password
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )

    submit = SubmitField('Update Profile')
