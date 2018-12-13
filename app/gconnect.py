import os

from flask import Flask, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import login_user

from app import app, user_store

app.secret_key = "supersekrit"

CLIENT_ID = '1099071368483-b5va6131038lda6ac1un62rufb5bfv69.apps.googleusercontent.com'
CLIENT_SECRET = '5ulFhoZUYU1Mw0pyaHCIBqdW'

blueprint = make_google_blueprint(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scope=[
        "https://www.googleapis.com/auth/plus.me",
        "https://www.googleapis.com/auth/userinfo.email",
    ]
)
app.register_blueprint(blueprint, url_prefix="/login")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

@app.route("/gconnect")
def index():

    # get the user email from google and check if it matches the user table in database
    # if found, he will logged in
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    user_email = resp.json()["email"]
    existing_user = user_store.get_by_email(user_email)
    if existing_user:
        login_user(existing_user, remember=True)
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))
