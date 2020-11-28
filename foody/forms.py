import os
import sys

from flask_wtf import FlaskForm
from flask_wtf.file import FileField

from wtforms import StringField, SubmitField, FloatField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length


class TableForm(FlaskForm):
    number_guests = IntegerField("Number of people:", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ProductUpload(FlaskForm):
    pname = StringField("Product Name", validators=[DataRequired()])
    pdescription = StringField("Description", validators=[DataRequired()])
    pprice = FloatField("Price", validators=[DataRequired()])
    pimage = FileField("Image of Product", validators=[DataRequired()])
    ptype = SelectField("Product Type", choices=[("Starter"), ("Main Course"), ("Dessert")])
    pgluten_free = SelectField("Gluten Free?", choices=[("Yes"), ("No")])
    plactose_free = SelectField("Lactose Free?", choices=[("Yes"), ("No")])
    pvegetarian = SelectField("Vegetarian?", choices=[("Yes"), ("No")])
    pvegan = SelectField("Vegan?", choices=[("Yes"), ("No")])
    submit_button = SubmitField("Go")
