from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, IntegerField, TextAreaField, PasswordField

from wtforms.validators import DataRequired, Length, Email



class TableForm(FlaskForm):
    number_guests = IntegerField("Number of people:", validators=[DataRequired()])
    submit = SubmitField("Submit")


class MenuForm(FlaskForm):

	name = StringField('name', validators=[DataRequired()])
	description = TextAreaField('Content', validators=[DataRequired(), Length(min=1, max=200)])
	submit = SubmitField('Save')

class AddAdmin(FlaskForm):
    full_name = StringField("full name", validators=[DataRequired()])
    email = StringField("email", validators=[DataRequired(), Email()])
    username = StringField("username", validators=[DataRequired()])
    password = PasswordField("password", validators = [DataRequired()])

class AdminLogin(FlaskForm):
     username=StringField("username", validators=[DataRequired()])
     password= PasswordField("password", validators=[DataRequired()])

