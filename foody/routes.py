import pandas as pd
import os
import sys
from flask import Flask, render_template, redirect, url_for, request, flash, session
from django.contrib.auth.decorators import login_required

from flask_wtf import FlaskForm
from flask_wtf.file import FileField

from wtforms import StringField, SubmitField, FloatField, IntegerField, TextAreaField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length, Email

from foody import app, db, data
from foody.forms import TableForm, ProductUpload, OrderFood  # MenuForm
from foody.models import Products, Table, add_order  # ,User, register_login


#from flask_login import LoginManager, UserMixin, login_user, current_user
#from flask_login import logout_user, login_required


##########
# Routes #
##########


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/during")
@login_required
def during():
    return render_template("during.html")


@app.route("/end")
def end():
    logout_user(user)
    return render_template("end.html")


@app.route("/add-admin-here-make-restricted", methods=["GET", "POST"])
def add_admin_route():
    """
    ADD THIS IN LATER FOR SECURITY
    if current_user.access_level = 3:
    """
    form = AddAdmin()
    if form.validate_on_submit():
        add_admin(form)
        return redirect(url_for("admin_login"))


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    form = AdminLogin()
    if form.validate_on_submit():
        if check_admin(form):
            return redirect(url_for("overview"))


@app.route("/overview", methods=["GET", "POST"])
@login_required
def overview():
    if current_user.access_level in [1, 2]:
        table_df = pd.read_sql(Table.query.statement, db.session.bind)
        return render_template("overview.html", df=table_df)


@app.route("/table/<table_number>", methods=["GET", "POST"])
def table(table_number):
    form = TableForm()
    table_number = table_number
    if form.validate_on_submit():
        register_login(form, table_number)
        return redirect(url_for("during"))
    return render_template("table.html", form=form, table_number=table_number)


@app.route("/upload-product", methods=["GET", "POST"])
def upload():
    form = ProductUpload()

    if form.validate_on_submit():

        f = form.pimage.data

        # this path is for saving a filepath to the csv file. This is also the
        # file path we will be using in the html to load the image
        path_in_static_folder = os.path.join("product_images", form.pname.data)

        # this is the path we will use to actually store the image
        filepath = os.path.join("foody/static", path_in_static_folder)

        f.save(filepath)

        product = Products(
            pname=form.pname.data,
            pdescription=form.pdescription.data,
            pprice=form.pprice.data,
            ptype=form.ptype.data,
            pvegan=form.pvegan.data,
            pvegetarian=form.pvegan.data,
            pgluten_free=form.pgluten_free.data,
            plactose_free=form.plactose_free.data
        )

        db.session.add(product)
        db.session.commit()
        global data  # global allows data to be modified inside function
        data = data.append({"name": form.pname.data,
                            "description": form.pdescription.data,
                            "price": form.pprice.data,
                            "img_path": path_in_static_folder},
                           ignore_index=True)

        data.to_csv("database.csv", index=False)

        return redirect(url_for("menu"))

    return render_template("menu/upload.html", form=form)


@app.route("/menu")
def menu():
    global data
    length = len(data)
    # return render_template("menu/menu.html", df=data, length=length)
    form = OrderFood()
    if form.validate_on_submit():
        add_order(form)
        flash("order submitted sucessfully")
    return render_template("menu/menu.html", df=data, length=length, form=form)


@app.route("/product/<product_name>")
def single_product(product_name):
    # we access the row of the dataframe that we want
    product_info = data.loc[data["name"] == product_name, :]
    # we transform the single row into a dictionary (this is easier to access in the html)
    # code from: https://stackoverflow.com/questions/50575802/convert-dataframe-row-to-dict
    product_info = product_info.to_dict('records')[0]
    return render_template("menu/single_item.html", product_info=product_info)


# @app.route("/order", methods=["GET", "POST"])
# # @login_required
# def order():
#     form = OrderFood()
#     if form.validate_on_submit():
#         add_order(form)
#         flash("order submitted sucessfully")
#     return render_template("order.html", form=form)
