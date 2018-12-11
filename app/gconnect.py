import os

from flask import json, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from flask_httpauth import HTTPBasicAuth
from flask_login import login_user
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError, TokenExpiredError

from app import app, user_store

auth = HTTPBasicAuth()
CLIENT_ID = '1099071368483-b5va6131038lda6ac1un62rufb5bfv69.apps.googleusercontent.com'

CLIENT_SECRET = '5ulFhoZUYU1Mw0pyaHCIBqdW'

APPLICATION_NAME = "ND_App"

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
        return "This URL is not authorized.", 405
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
    # or maybe any OAuth2Error
    except (InvalidGrantError, TokenExpiredError) as e:
        return redirect(url_for('login'))
