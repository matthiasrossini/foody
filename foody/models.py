from itsdangerous import TimedJSONWebSignatureSerializer as Serializer #function within flask to allow secure & time sensitive token creation
import datetime
from foody import db, login_manager
from flask import current_app, flash
from flask_login import UserMixin, current_user, login_user #UserMixin makes user mgmt easier, not quite sure how this works tho
import uuid
import bcrypt

###########
# Models  #
###########

# user_loader helper function for the login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# This is actually to create the column in the database

class User(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)
    number_guests = db.Column(db.Integer, nullable=False)
    uuid_table=db.Column(db.String(60), nullable=False)
    date=db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    access_level=db.Column(db.Integer, nullable=False)
    def __repr__(self):
            return f"User(id: {self.id}, table number: {self.table_number}"+\
                   f" number of guests: {self.number_guests}, date: {self.date})"

#class of waiter than can access overview of tables
class Waiter(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(60), nullable=False)
    password=db.Column(db.String(30), nullable=False)
    access_level=db.Column(db.Integer, nullable=False)


#class of admin that can upload new products and see overview of tables
class Admin(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(60), nullable=False)
    password=db.Column(db.String(30), nullable=False)
    full_name= db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(60), nullable=False)
    access_level=db.Column(db.Integer, nullable=False)



# this is to insert in the database what the user has input
def register_login(form, table_number):
    uuid_table = str(uuid.uuid1())
    table = User(
        table_number=table_number,
        number_guests=form.number_guests.data,
        uuid_table= uuid_table,
        access_level=0
    	)
    db.create_all()
    db.session.add(table)
    db.session.commit()
"""
add in not possible to have two tablennumbers loggin in same time
+
menu route accessible for all people
"""
    user=User.query.filter_by(uuid_table=uuid_table).first()
    login_user(user)


#this is to add in new admins
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
                    full_name = form.full_name.data,
                    email=form.email.data,
                    username=form.username.data,
                    password=hashed_password,
                    access_level=2
                    )
    db.create_all()
    db.session.add(new_admin)
    db.session.commit()

#this is to check that the admin login is correct and log them in
def check_admin(form):
    username= form.username.data
    admin = Admin.query.filter_by(username=username).first()

    if admin is not None:
        if bcypt.check_password_hash(form.password.data, admin.password):
            login_user(admin)
            return True


#this is to check the waiter login


