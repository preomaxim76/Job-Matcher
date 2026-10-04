from flask import Flask, render_template, request, redirect, session, flash
from functools import wraps
from dotenv import load_dotenv
import os
from authlib.integrations.flask_client import OAuth

load_dotenv()

def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return function(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
app.secret_key = os.environ["SESSION_KEY"]

# Connection google
oauth = OAuth(app)
# Adding google as oath provider
google = oauth.register(
    name="google",
    client_id=os.environ["GOOGLE_CLIENT_ID"],
    client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    # Forget any user
    session.clear()

    if request.method == "POST":
        action = request.form.get("action")
        if not action:
            username, password = request.form.get("username"), request.form.get("password")

            # TODO: Check user's username and password

            session["user_id"] = ... # TODO: add user_id, got from the SQL database

            return redirect("/")

        return google.authorize_redirect("http://localhost:5000/auth/google/callback")
    else:
        return render_template("login.html", show_nav=False)

@app.route("/auth/google/callback")
def google_callback():
    token = google.authorize_access_token()
    user = token["userinfo"]    
    # if Google's own id for user is in our database - get data
    if user["sub"] in ...:
        pass
    
    else:
        pass