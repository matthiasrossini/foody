from itsdangerous import TimedJSONWebSignatureSerializer as Serializer #function within flask to allow secure & time sensitive token creation
import datetime
from foody import db, login_manager
from flask import current_app
from flask_login import UserMixin, current_user, login_user #UserMixin makes user mgmt easier, not quite sure how this works tho
import uuid

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
    def __repr__(self):
            return f"User(id: {self.id}, table number: {self.table_number}"+\
                   f" number of guests: {self.number_guests}, date: {self.date})"

class Admin(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(60), nullable=False)
    password=db.Column(db.String(30), nullable=False)

# this is to insert in the database what the user has input
def register_login(form, table_number):
    uuid_table = str(uuid.uuid1())
    table = User(
        table_number=table_number,
        number_guests=form.number_guests.data,
        uuid_table= uuid_table
    	)
    db.create_all()
    db.session.add(table)
    db.session.commit()

    user=User.query.filter_by(uuid_table=uuid_table).first()
    login_user(user)



