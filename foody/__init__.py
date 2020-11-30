import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user
from flask_login import logout_user, login_required
from google.cloud import storage
from foody.secrets import SQL_PASSWORD, SQL_PUBLIC_IP, SQL_DATABASE_NAME

app = Flask(__name__)

app.config["SECRET_KEY"]= "9289hab_wfdyqpvsa9ah-awf9AWdbzz"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
#setup database
db = SQLAlchemy(app)

#LoginManager + Bcrypt for hashing passwords
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = 'info' #add better style
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

from foody import routes