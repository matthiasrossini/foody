import os
import sys

from flask_wtf import FlaskForm
from flask_wtf.file import FileField

from wtforms import StringField, SubmitField, FloatField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length


class TableForm(FlaskForm):
    number_guests = IntegerField("Number of people:", validators=[DataRequired()])
    submit = SubmitField("Submit")


class MenuForm(FlaskForm):
	name = StringField('name', validators=[DataRequired()])
	description = TextAreaField('Content', validators=[DataRequired(), Length(min=1, max=200)])
	submit = SubmitField('Save')


class MenuForm(FlaskForm):
    pname = StringField("Product Name", validators=[DataRequired()])
    pdescription = StringField("Description", validators=[DataRequired()])
    pprice = FloatField("Price", validators=[DataRequired()])
    pimage = FileField("Image of Product", validators=[DataRequired()])
    submit_button = SubmitField("Go")