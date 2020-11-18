from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length

class TableForm(FlaskForm):
    number_guests = IntegerField("Number of people:", validators=[DataRequired()])
    submit = SubmitField("Submit")

class MenuForm(FlaskForm):
	name = StringField('name', validators=[DataRequired()])
	description = TextAreaField('Content', validators=[DataRequired(), Length(min=1, max=200)])
	submit = SubmitField('Save')