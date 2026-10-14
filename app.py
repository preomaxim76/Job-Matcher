from flask import Flask, render_template, request, redirect, session, flash, url_for
from functools import wraps
from dotenv import load_dotenv
import os
from authlib.integrations.flask_client import OAuth
import sqlite3
from datetime import datetime
import bcrypt
import resend
from itsdangerous import URLSafeTimedSerializer

load_dotenv()

# Connect database
def connect_database(db: str):
    conn = sqlite3.connect(db)
    # To use it like a dict
    conn.row_factory = sqlite3.Row
    return conn

# Decorator function
def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None and session.get("google_id") is None:
            return redirect("/landing_page")
        return function(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
# To use flask's sessions
app.secret_key = os.environ["SESSION_KEY"]

# To use resend (sending verification emails)
resend.api_key = os.environ["RESEND_API_KEY"]

# Connect google
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

        
# Creating an object that creates urls
serializer = URLSafeTimedSerializer(
    app.secret_key
)

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/landing_page")
def landing_page():
    return render_template("landing_page.html", show_nav="False")

@app.route("/login", methods=["POST", "GET"])
def login():
    # Got data from the form, submitted by the user in /login
    if request.method == "POST":
        action = request.form.get("action")
        # If logged in without google, traditionally
        if not action:
            email, password = request.form.get("email"), request.form.get("password")

            conn = connect_database("users.db")
            c = conn.cursor()
            
            db_password = c.execute("SELECT password FROM users WHERE email = ?", (email, )).fetchone()
            # If no such user at all
            if not db_password:
                flash("Incorrect email or password.", "error")
                conn.close()
                return redirect("/login")

            # Get the password from the list [password]
            db_password = db_password[0]
            
            # Checking if passwords match
            if not bcrypt.checkpw(password.encode("utf-8"), db_password):
                flash("Incorrect email or password.", "error")
                conn.close()
                return redirect("/login")
            
            # Adding user_id to session
            session["user_id"] = c.execute("SELECT user_id FROM users WHERE email = ?", (email, )).fetchone()[0]
            conn.close()

            return redirect("/")
        
        # If logged in with google 
        return google.authorize_redirect("http://127.0.0.1:5000/auth/google/callback") # Special url - created at google cloud console
    
    else:
        return render_template("login.html", show_nav=False)

@app.route("/auth/google/callback")
# Redirected to "http://127.0.0.1:5000/auth/google/callback"
def google_callback():
    time = datetime.now()
    # Gives google code in exchange for token
    token = google.authorize_access_token()
    user = token["userinfo"]    

    conn = connect_database("users.db")
    c = conn.cursor()

    db_user_id = c.execute("SELECT user_id FROM users WHERE email = ?", (user["email"], )).fetchone()
    # Check if user has registered, using email and password with that email
    if db_user_id:
        session["user_id"] = db_user_id[0]
        conn.close()
        flash("You have successfully logged in!", "success")
        return redirect("/")

    # if Google's own id for user is in our database - get data
    user_info = c.execute("SELECT * FROM users WHERE google_id = ?", (user["sub"], )).fetchone()

    # User is already registered
    if user_info:
        session["user_id"] = user_info["user_id"]
        flash("You have successfully logged in!", "success")
        
    # User has to be added
    else:
        c.execute("INSERT INTO users (email, google_id, created_at, username) VALUES (?, ?, ?, ?)", (user["email"], user["sub"], time, user["name"]))
        conn.commit()

        session["user_id"] = c.execute("SELECT user_id FROM users WHERE username = ?", (user["name"],)).fetchone()[0]
        flash("You have successfully registered!", "success")
        
    conn.close()
    return redirect("/")

@app.route("/register", methods=["POST", "GET"])
def register():
    # Getting form user filled at /register
    if request.method == "POST":
        time = datetime.now()
        email = request.form.get("email")
        
        if not email.endswith("@gmail.com"):
            flash("Email is not valid. Please enter a valid one.", "error")
            return redirect("/register")

        # Checking if there already is an account with that email
        conn = connect_database("users.db")
        c = conn.cursor()
        if c.execute("SELECT email FROM users WHERE email = ?", (email, )).fetchall() != []:
            flash("This email is linked to an existing account. Please log in with it.", "error")
            conn.close()
            return redirect("/login")

        username = request.form.get("username")
        # Username should have some alphabetic character and should be < 19 but > 2
        if username.isdigit() or not (2 < len(username) < 19):
            flash("Please enter a valid username!", "error")
            return redirect("/register")

        # Password's length should be in range 4-18
        password = request.form.get("password")
        if not (3 < len(password) < 19):
            flash("Your password's length should be in range 4 - 18!", "error")
            conn.close()
            return redirect("/register")

        # Checking if confirmation and password match
        confirmation = request.form.get("password_confirmation")
        if password != confirmation:
            flash("Passwords do not match!", "error")
            conn.close()
            return redirect("/register")

        # Hash password to keep it secret in the database
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        c.execute("INSERT INTO users (email, password, created_at, username) VALUES (?, ?, ?, ?)", (email, hashed_password, time, username))
        conn.commit()
        
        session["user_id"] = c.execute("SELECT user_id FROM users WHERE username = ?", (username, )).fetchone()[0]
        conn.close()

        # After saving checking wether email is valid (then we'll delete it if not)
        token = serializer.dumps(email, salt="email_verification")
        
        # Verification url with the whole route (.../verify_email/...)
        verification_url = url_for("verify_email", token=token, _external=True)

        r = resend.Emails.send({
            "from": "Job Matcher <onboarding@resend.dev>",
            "to": email,
            "subject": "Verify your email.",
            "html": f"""
                <p>Hello!</p>
                <p>Follow this link to verify your email</p>
                <a href="{verification_url}">Verify Email</a>"""
            })

        print(r)

        flash("Verification link sent. Check your inbox.", "success")

        return redirect("/login")

    else:
        return render_template("register.html")

@app.route("/verify_email/<token>")
def verify_email(token):
    try:
        # max_age = 1 hour
        # Verifying
        email = serializer.loads(
            token, 
            salt="email_verification",
            max_age=3600
        )

        flash("You have successfully registered!", "success")

        return redirect("/")

    except:
        flash("Invalid or expired link", "error")

        # Remove user from the table
        conn = connect_database("users.db")
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE user_id = ?", (session["user_id"], ))
        conn.commit()
        conn.close()

        session.clear()

        flash("Link expired or invalid.", "error")

        return redirect("/register")

@app.route("/learn_more")
def learn_more():
    return render_template("learn_more.html")

@app.route("/forgot_password")
def forgot_password():
    return render_template("forgot_password.html")