from itsdangerous import TimedJSONWebSignatureSerializer as Serializer #function within flask to allow secure & time sensitive token creation 
from datetime import datetime #time from local server
from foody import db, login_manager
from flask import current_app
from flask_login import UserMixin, current_user #UserMixin makes user mgmt easier, not quite sure how this works tho

###########
# Models  #
###########

# user_loader helper function for the login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# This is actually to create the column in the database
class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)
    taken = db.Column(db.String(10), nullable=False)
    number_guests = db.Column(db.Integer)

# this is to insert in the database what the user has input
def register(form, table_number):
    table = Table(
        table_number=table_number,
        number_guests=form.number_guests.data,
        taken="yes" 
    	)
    db.session.add(table)
    db.session.commit()

