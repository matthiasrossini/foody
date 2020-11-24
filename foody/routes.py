from flask import Flask, render_template, redirect, url_for
from foody import app, db
from foody.forms import TableForm, MenuForm
from foody.models import load_user, User, register_login
from flask_login import LoginManager, UserMixin, login_user, current_user
from flask_login import logout_user, login_required
import pandas as pd

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

@app.route("/overview", methods=["GET", "POST"])
@login_required
def overview():
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