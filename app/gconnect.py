import os

from flask import json, redirect, url_for, jsonify
from flask_login import login_user

from app import app, user_store
from flask_dance.contrib.google import make_google_blueprint, google
from flask_httpauth import HTTPBasicAuth
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError, TokenExpiredError, OAuth2Error

auth = HTTPBasicAuth()
CLIENT_ID = json.loads(
    open('app/client_secrets.json', 'r').read())['web']['client_id']

CLIENT_SECRET = json.loads(
    open('app/client_secrets.json', 'r').read())['web']['client_secret']

APPLICATION_NAME = "MyNanoCatalogApp"

blueprint = make_google_blueprint(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scope=[
        "https://www.googleapis.com/auth/plus.me",
        "https://www.googleapis.com/auth/userinfo.email",
    ]
)

app.register_blueprint(blueprint, url_prefix='/login')
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


# login using google
# the user should have already signed up with google email!

@app.route("/gconnect")
def google_connect():
    if not google.authorized:
        return redirect(url_for("login"))
    try:
        resp = google.get("/plus/v1/people/me")
        assert resp.ok, resp.text
        user_email = resp.json()["emails"][0]['value']

        existing_user = user_store.get_by_email(user_email)
        if existing_user:
            login_user(existing_user, remember=True)
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))

    except (InvalidGrantError, TokenExpiredError) as e:  # or maybe any OAuth2Error
        return redirect(url_for('login'))

