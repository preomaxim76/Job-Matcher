from flask import Flask, render_template, request, redirect, session, flash
from functools import wraps
from dotenv import load_dotenv
import os
from authlib.integrations.flask_client import OAuth
import sqlite3
from datetime import datetime
import bcrypt

load_dotenv()

# Connect database
def connect_database(db: str):
    conn = sqlite3.connect(db)
    return conn

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

            conn = connect_database("users.db")
            c = conn.cursor()

            db_password = c.execute("SELECT password FROM users WHERE username = ?", (username, )).fetchone()[0]

            if not bcrypt.checkpw(password.encode("utf-8"), db_password):
                flash("Incorrect username or password...")
                conn.close()
                return redirect("/login")
            

            session["user_id"] = c.execute("SELECT user_id FROM users WHERE username = ?", (username, )).fetchone()

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

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        time = datetime.now()
        username = request.form.get("username")
        if username.isdigit() or not (2 < len(username) < 18):
            flash("Please enter a valid username!", "error")
            return redirect("/register")

        conn = connect_database("users.db")
        c = conn.cursor()
        if c.execute("SELECT username FROM users WHERE username = ?", (username, )).fetchall() != []:
            flash("Username is not available. Please choose a different one.", "error")
            conn.close()
            return redirect("/register")

        password = request.form.get("password")
        if not (3 < len(password) < 19):
            flash("Your password's length should be in range 4 - 18!", "error")
            conn.close()
            return redirect("/register")
        confirmation = request.form.get("password_confirmation")
        
        if password != confirmation:
            flash("Passwords do not match!", "error")
            conn.close()
            return redirect("/register")
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        c.execute("INSERT INTO users (password, created_at, username) VALUES (?, ?, ?)", (hashed_password, time, username))
        conn.commit()
        
        session["user_id"] = c.execute("SELECT user_id FROM users WHERE username = ?", (username, )).fetchone()[0]
        conn.close()

        return redirect("/")

    else:
        return render_template("register.html")