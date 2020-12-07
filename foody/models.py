# function within flask to allow secure & time sensitive token crea
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime  # time from local server
from flask import current_app, flash, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, current_user
from flask_login import logout_user, login_required
from foody import login_manager, db
import uuid
import bcrypt
import pandas as pd
from sqlalchemy.orm import validates
from flask_sqlalchemy import SQLAlchemy
from google.cloud import storage
###########
# Models  #
###########


# setup LoginManager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# class Table(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     table_number = db.Column(db.Integer, nullable=False)
#     taken = db.Column(db.String(10), nullable=False)
#     number_guests = db.Column(db.Integer)
#     ptype = db.Column(db.String(20))
#     pgluten_free = db.Column(db.String(10))
#     plactose_free = db.Column(db.String(10))
#     pvegetarian = db.Column(db.String(10))
#     pvegan = db.Column(db.String(10))
#     # user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False) --> backref needed for waiters view


class Orders(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    food = db.Column(db.String)
    price = db.Column(db.Integer)
    uuid = db.Column(db.Integer)
    user_table = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    @validates('food')
    def convert_upper(self, key, value):
        return value.upper()


class Products(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    pname = db.Column(db.String(50), unique=True, nullable=False)
    pdescription = db.Column(db.String(100), nullable=False)
    pprice = db.Column(db.Integer, nullable=False)
    ptype = db.Column(db.String)
    pgluten_free = db.Column(db.String)
    plactose_free = db.Column(db.String)
    pvegan = db.Column(db.String)
    pvegetarian = db.Column(db.String)
    img_public_url = db.Column(db.String(300), nullable=False)
    pimage = db.Column(db.String)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)

    @validates('pname')
    def convert_upper(self, key, value):
        return value.upper()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer)
    number_guests = db.Column(db.Integer)
    full_name = db.Column(db.String(50))
    username = db.Column(db.String(60))
    password = db.Column(db.String(200))
    email = db.Column(db.String(60))
    uuid = db.Column(db.String(60))
    client_is_gone = db.Column(db.String(5))
    date = db.Column(db.DateTime, default=datetime.now)
    role = db.Column(db.String(20), nullable=False)
    orders = db.relationship("Orders", backref="table", lazy=True)
    #output1 = (f" User ID: {self.id}, table number: {self.table_number} ")
    #output2 = (f" Number of guests: {self.number_guests}, date: {self.date} ")
    # def __repr__(self):
    # return output1 + output2

# this is to insert in the database what the user has input


def register_login(form, table_number):
    uuid_table = str(uuid.uuid1())
    table = User(
        uuid=uuid_table,
        table_number=table_number,
        role="client",
    )
    db.session.add(table)
    db.session.commit()

    user = User.query.filter_by(uuid=uuid_table).first()
    login_user(user)


# Getting products from SQL
def get_products():
    df = pd.read_sql(Products.query.statement, db.session.bind)

    return df

# Getting orders from SQL


def get_orders():
    df1 = pd.read_sql(Orders.query.statement, db.session.bind)

    return df1

# this is to add in new admins


def add_admin(form):
    admin_username = form.username.data

    if User.query.filter_by(username=admin_username).count():
        flash("username is taken. Try another one.")
        return False
    if User.query.filter_by(email=form.email.data).count():
        flash("This email is already taken! Please pick another.")
        return False
    salt = bcrypt.gensalt()
    password = form.password.data.encode("utf-8")
    hashed_password = bcrypt.hashpw(password, salt).decode("utf-8")
    print(hashed_password)

    new_admin = User(
        full_name=form.full_name.data,
        email=form.email.data,
        username=form.username.data,
        password=hashed_password,
        role="admin"
    )
    db.session.add(new_admin)
    db.session.commit()

    return True


# this is to check that the admin login is correct and log them in
def check_admin(form):
    username = form.username.data
    admin = User.query.filter_by(username=username).first()

    if admin is not None:
        if bcrypt.checkpw(form.password.data.encode("utf-8"), admin.password.encode("utf-8")):
            login_user(admin)
            return True
        else:
            flash("password mistake")
            return redirect(url_for("admin_login"))

    else:
        flash("Admin not in database. Check credentials")
        return redirect(url_for("admin_login"))


# this is to add waiters


def add_waiter(form):
    waiter_username = form.username.data

    if User.query.filter_by(username=waiter_username).count():
        flash("Username is taken. Try another one.")
        return False
    salt = bcrypt.gensalt()
    password = form.password.data.encode("utf-8")
    hashed_password = bcrypt.hashpw(password, salt).decode("utf-8")

    new_waiter = User(
        full_name=form.full_name.data,
        username=form.username.data,
        password=hashed_password,
        role="waiter"
    )
    db.session.add(new_waiter)
    db.session.commit()

# this is to check the waiter login


# this is to check the waiter login
def check_waiter(form):
    username = form.username.data
    password = form.password.data.encode("utf-8")
    waiter = User.query.filter_by(username=username).first()

    if waiter is not None:
        if bcrypt.checkpw(password, waiter.password.encode("utf-8")):
            login_user(waiter)
            return True


# This logs the client out and sets his client_is_gone to "yes"
# Doing so ensures this table doesn't show up in the "overview" page


def logout_client():
    if current_user.role == "client":
        user = User.query.filter_by(uuid=current_user.uuid).first()
        user.client_is_gone = "yes"
        db.session.commit()
        logout_user()
    else:
        return redirect(url_for("logout"))


# for pics to bucket


def upload_bytes_to_gcs(bucket_name, bytes_data, destination_blob_name):

    storage_client = storage.Client()

    # get the bucket by name
    bucket = storage_client.bucket(bucket_name)

    # this creates the blob object in python but does not upload anything
    blob = bucket.blob(destination_blob_name)

    # upload the file
    blob.upload_from_string(bytes_data)

    # set the image to be publicly viewable
    blob.make_public()

    # get publicly viewable image of url
    public_img_url = blob.public_url

    return public_img_url
