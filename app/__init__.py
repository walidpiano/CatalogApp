from flask import Flask, json
from flask_httpauth import HTTPBasicAuth

from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

from app import stores

from app.models import User, Item, Category


category_store = stores.CategoryStore()
item_store = stores.ItemStore()
user_store = stores.UserStore()

CLIENT_SECRET_FILE = 'app/client_secret.json'

from app import views
from app import api
from app import gconnect
