# function within flask to allow secure & time sensitive token crea
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime  # time from local server
from foody import db, login_manager
from flask import current_app, flash
from flask_login import UserMixin, current_user, login_user
import uuid
import bcrypt


###########
# Models  #
###########


# user_loader helper function for the login manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)
    taken = db.Column(db.String(10), nullable=False)
    number_guests = db.Column(db.Integer)
    orders = db.Column(db.Integer)
    ptype = db.Column(db.String(20))
    pgluten_free = db.Column(db.String(10))
    plactose_free = db.Column(db.String(10))
    pvegetarian = db.Column(db.String(10))
    pvegan = db.Column(db.String(10))


class Products(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    pname = db.Column(db.String(30), unique=True, nullable=False)
    pdescription = db.Column(db.String(30), nullable=False)
    pprice = db.Column(db.Integer, nullable=False)
    ptype = db.Column(db.String)
    pgluten_free = db.Column(db.String)
    plactose_free = db.Column(db.String)
    pvegan = db.Column(db.String)
    pvegetarian = db.Column(db.String)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("user_id"), nullable=False)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)
    number_guests = db.Column(db.Integer, nullable=False)
    uuid_table = db.Column(db.String(60), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    access_level = db.Column(db.Integer, nullable=False)

    #output1 = (f" User ID: {self.id}, table number: {self.table_number} ")
    #output2 = (f" Number of guests: {self.number_guests}, date: {self.date} ")

    # def __repr__(self):
    # return output1 + output2


# class of waiter than can access overview of tables
class Waiter(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    access_level = db.Column(db.Integer, nullable=False)


# class of admin that can upload new products and see overview of tables
class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    full_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(60), nullable=False)
    access_level = db.Column(db.Integer, nullable=False)


# this is to insert in the database what the user has input
def register_login(form, table_number):
    uuid_table = str(uuid.uuid1())
    table = User(
        table_number=table_number,
        number_guests=form.number_guests.data,
        taken="yes"
    )
    db.session.add(table)
    db.session.commit(
        uuid_table=uuid_table,
        access_level=0
    )
    db.create_all()
    db.session.add(table)
    db.session.commit()

    user = User.query.filter_by(uuid_table=uuid_table).first()
    login_user(user)


# this is to add in new admins
def add_admin(form):
    admin_username = form.username.data

    if Admin.query.filter_by(username=admin_username).count():
        flash("username is taken. Try another one.")
        return False
    if Admin.query.filter_by(email=form.email.data).count():
        flash("This email is already taken! Please pick another.")
        return False

    hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

    new_admin = Admin(
        full_name=form.full_name.data,
        email=form.email.data,
        username=form.username.data,
        password=hashed_password,
        access_level=2
    )
    db.create_all()
    db.session.add(new_admin)
    db.session.commit()

# this is to check that the admin login is correct and log them in


def admin_login(form):
    username = form.username.data
    admin = Admin.query.filter_by(username=username).first()

    if admin is not None:
        if bcypt.check_password_hash(form.password.data, admin.password):
            login_user(admin)
            return True

# this is to check the waiter login


def add_order(form):
    order = Table(order=form.order.data)
    db.session.add(order)
    db.session.commit()
