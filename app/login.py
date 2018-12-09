import json
import string
from os import abort
import os
import string
import httplib2
import requests
from flask import Flask, render_template, request, jsonify, make_response, g, redirect, url_for
from flask_httpauth import HTTPBasicAuth
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_dance.contrib.google import make_google_blueprint, google
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError, TokenExpiredError, OAuth2Error
import json

from flask import Blueprint, request, url_for, redirect, render_template, flash
from flask_wtf.csrf import CSRFProtect
from flask_login import current_user, login_user, logout_user, LoginManager, \
                        login_required
from werkzeug.security import generate_password_hash, check_password_hash
from oauth2client import client
import random
from app.models import base, Category, Item, User

auth = Blueprint('auth', __name__)

# Load CSRFProtect and LoginManager
csrf = CSRFProtect()
login_manager = LoginManager()

# Set the default route for login form to auth.login
login_manager.login_view = "auth.login"


# https://flask-login.readthedocs.io/en/latest/#flask_login.LoginManager.user_loader
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


#auth = HTTPBasicAuth()

CLIENT_ID = json.loads(
    open('app/client_secrets.json', 'r').read())['web']['client_id']

CLIENT_SECRET = json.loads(
    open('app/client_secrets.json', 'r').read())['web']['client_secret']


APPLICATION_NAME = "MyNanoCatalogApp"

app = Flask(__name__)
app.secret_key = "supersekrit"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


blueprint = make_google_blueprint(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scope=[
        "https://www.googleapis.com/auth/plus.me",
        "https://www.googleapis.com/auth/userinfo.email",
    ]
)
app.register_blueprint(blueprint, url_prefix="/login")


@app.route('/')
@app.route('/home')
@app.route('/index')
@auth.login_required
def show_home():

    if g.user is None:
        return render_template('index.html', current_user='')
    else:
        return render_template('index.html', current_user=g.user.username)


@app.route('/logout')
def logout():

    g.user = None
    return redirect(url_for('show_home'))


@app.route("/login/access")
def index():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    return "You are {email} on Google".format(email=resp.json()["email"])


engine = create_engine('sqlite:///sys_database.db')
base.metadata.bind = engine

db_session = sessionmaker(bind=engine)
session = db_session()


# from app import dummy_data

@app.route('/catalog/<string:category>/items')
def show_catalog(category):
    category_id = get_category_id(category)
    items = session.query(Item).filter_by(category_id=category_id).order_by(Item.id.desc()).all()
    return render_template('category.html', category=category, items=items)


@app.route('/catalog/<string:category_name>/<string:item_name>')
def show_item(category_name, item_name):
    category_id = get_category_id(category_name)
    item = session.query(Item).filter_by(category_id=category_id, name=item_name).first()
    return render_template('item.html', item=item, category=category_name)


def get_all_categories():
    return session.query(Category).order_by(Category.name).all()


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        print('yes')
        return render_template('login.html')
    elif request.method == 'POST':
        print('no')
        username = request.form['username']
        password = request.form['password']
        user = User(username=username)
        logged_user = verify_password(username,password)
        if logged_user:
            print(logged_user)
            print(str.title(logged_user.username))
            current_user = str.title(logged_user.username)
        return redirect(url_for('show_home', current_user=current_user))


@app.route('/signup')
def sign_up():
    return render_template('signup.html')


@app.route('/api/last/items')
def get_all_last_items():
    categories = get_all_categories()
    list_items = []

    for category in categories:
        selected_id = category.id
        item = get_last_item(selected_id)

        list_items.append({
            "category_id": item[0],
            "category_name": category.name,
            "item_id": item[2],
            "item_name": item[1]
        })

    return jsonify(list_items)


def get_last_item(category_id):
    item = session.query(Item).filter_by(category_id=category_id).order_by(Item.id.desc()).first()
    if item:
        return [item.category_id, item.name, item.id]
    else:
        return [category_id, 'No Items', '#']


def get_category_id(category_name):
    category = session.query(Category).filter_by(name=category_name).first()
    return category.id


@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    new_user = User(username=username, email=email)
    new_user.hash_password(password)
    session.add(new_user)
    session.commit()

    return redirect(url_for('show_home'))


@auth.verify_password
def verify_password(username_or_token, password):
    # Try to see if it's a token first
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id=user_id).one()
    else:
        user = session.query(User).filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return None
    g.user = user

    return user


if __name__ == "__main__":
    app.run()

