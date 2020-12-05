import os
import sys

from flask_wtf import FlaskForm
from flask_wtf.file import FileField

from wtforms import StringField, SubmitField, FloatField, IntegerField, TextAreaField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length, Email, InputRequired


class TableForm(FlaskForm):
    table_number = IntegerField("Table number:", validators=[DataRequired()])
    number_guests = IntegerField("Number of people:", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ProductUpload(FlaskForm):
    pname = StringField("Product Name", validators=[DataRequired()])
    pdescription = StringField("Description", validators=[DataRequired()])
    pprice = FloatField("Price", validators=[DataRequired()])
    ptype = SelectField("Which Course: ", choices=[
                        ("starter", "Starter"), ("main", "Main Course"), ("dessert", "Dessert")])
    pgluten_free = SelectField("Gluten Free?", choices=[("no", "No"), ("yes", "Yes")])
    plactose_free = SelectField("Lactose Free?", choices=[("no", "No"), ("yes", "Yes")])
    pvegetarian = SelectField("Vegetarian?", choices=[("no", "No"), ("yes", "Yes")])
    pvegan = SelectField("Vegan?", choices=[("no", "No"), ("yes", "Yes")])
    pimage = FileField("Image of Product", validators=[DataRequired()])
    submit_button = SubmitField("Go")


class MenuForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    description = TextAreaField('Content', validators=[DataRequired(), Length(min=1, max=200)])
    submit = SubmitField('Save')


class AddAdmin(FlaskForm):
    full_name = StringField("full name", validators=[DataRequired()])
    email = StringField("email", validators=[DataRequired(), Email()])
    username = StringField("username", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("OK")


class AdminLogin(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("OK")


class AddWaiter(FlaskForm):
    full_name = StringField("full name", validators=[DataRequired()])
    username = StringField("username", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("OK")


class WaiterLogin(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("OK")


class StarterOrder(FlaskForm):
    Starters = SelectField("Select your Starter")
    Main = SelectField("Select your Main", validators=[InputRequired()])
    Dessert = SelectField("Select your Dessert")
    submit_button = SubmitField("Submit order")


class MainOrder(FlaskForm):
    Main = SelectField("Select your Main")
    submit_button = SubmitField("Submit order")


class DessertOrder(FlaskForm):
    Dessert = SelectField("Select your Dessert")
    submit_button = SubmitField("Submit order")
