from flask import Flask, render_template, redirect, url_for, request
from foody import app, db, data
from foody.forms import TableForm, ProductUpload
from foody.models import load_user, Table, register
import pandas as pd
import os
import sys


##########
# Routes #
##########


@app.route("/")
@app.route("/home")
def home():
	return render_template('home.html')


@app.route("/during")
def during():
    return render_template("during.html")


@app.route("/end")
def end():
    return render_template("end.html")


@app.route("/overview", methods=["GET", "POST"])
def overview():
    table_df = pd.read_sql(Table.query.statement, db.session.bind)
    return render_template("overview.html", df=table_df)


@app.route("/table/<table_number>", methods=["GET", "POST"])
def table(table_number):
    form = TableForm()
    table_number = table_number
    if form.validate_on_submit():
        register(form, table_number)
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

        global data #global allows data to be modified inside function
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
    return render_template("menu/menu.html", df=data, length=length)


@app.route("/product/<product_name>")
def single_product(product_name):
    # we access the row of the dataframe that we want
    product_info = data.loc[data["name"] == product_name, :]
    # we transform the single row into a dictionary (this is easier to access in the html)
    # code from: https://stackoverflow.com/questions/50575802/convert-dataframe-row-to-dict
    product_info = product_info.to_dict('records')[0]
    return render_template("menu/single_item.html", product_info=product_info)