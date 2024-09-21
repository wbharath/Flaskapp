from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, RadioField, SelectField, DecimalField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileAllowed



class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('User', 'User'), ('Webmaster', 'Webmaster')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
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
    artist_birth = StringField('Artist Birth', validators=[DataRequired()])
    artist_death = StringField('Artist Death')
    email = StringField('Artist Email', validators=[Email()])
    phone = StringField('Phone Number')
    nscc_location = StringField('NSCC Location', validators=[DataRequired()])
    initial_appraisal = DecimalField('Initial Appraisal', validators=[DataRequired()])
    new_appraisal = DecimalField('New Appraisal')
    purchase_price = DecimalField('Purchase Price', validators=[DataRequired()])
    relevant_contact_info = StringField('Relevant Contact Info', validators=[DataRequired()])
    provenance = StringField('Provenance')
    picture = FileField('Art Image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])


class MinimalForm(FlaskForm):
    title = StringField('Art Title')
    submit = SubmitField('Submit')