import os
from flask import Flask, request
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user
from flask_login import logout_user, login_required
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = "hard-to-guess-string"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

#setup database
db = SQLAlchemy(app)
#data = pd.read_csv("database.csv", sep=",")

#LoginManager + Bcrypt for hashing passwords
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = 'info' #add better style
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

from foody import routes