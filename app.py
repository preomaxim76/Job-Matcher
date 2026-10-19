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

def password_is_valid(password, confirmation):
    if len(password) < 6:
        return "Password's length is less than 6."

    if len(password) > 18:
        return "Password's length is more than 18."

    if password.isalpha():
        return "Password should have at least 1 digit."

    if password != confirmation:
        return "Passwords do not match."

    return True

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
    return render_template("index.html", show_nav=True)

@app.route("/landing_page")
def landing_page():
    return render_template("landing_page.html")

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
            
            # If user registered using google (didn't create password)
            if not db_password["password"]:
                flash("This account has been registered via google. Please log in using google.", "error")
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
        return render_template("login.html")

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

        session["user_id"] = c.execute("SELECT user_id FROM users WHERE email = ?", (user["email"],)).fetchone()[0]
        flash("You have successfully registered!", "success")
        
    conn.close()
    return redirect("/")

@app.route("/register", methods=["POST", "GET"])
def register():
    # Getting form user filled at /register
    if request.method == "POST":
        time = datetime.now()
        email = request.form.get("email")

        if not email:
            flash("Email is missing.", "error")
            return redirect("/register")
        
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
        if not username:
            flash("Username is missing.", "error")
            return redirect("/register")
        # Username should have some alphabetic character and should be < 19 but > 2
        if username.isdigit() or not (2 < len(username) < 19):
            flash("Please enter a valid username!", "error")
            return redirect("/register")

        password = request.form.get("password")
        if not password:
            flash("Password is missing.", "error")
            return redirect("/register")
        
        confirmation = request.form.get("password_confirmation")
        if not confirmation:
            flash("Password confirmation is missing.", "error")
            return redirect("/register")

        is_valid = password_is_valid(password, confirmation)

        if is_valid != True:
            flash(is_valid, "error")
            conn.close()
            return redirect("/register")

        # Hash password to keep it secret in the database
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        c.execute("INSERT INTO users (email, password, created_at, username) VALUES (?, ?, ?, ?)", (email, hashed_password, time, username))
        conn.commit()
        
        session["user_id"] = c.execute("SELECT user_id FROM users WHERE email = ?", (email, )).fetchone()[0]
        conn.close()

        # After saving check wether email is valid (then we'll delete it if not)
        token = serializer.dumps(email, salt="email_verification")
        
        # Verification url with the whole route (.../verify_email/...)
        verification_url = url_for("verify_email_registration", token=token, _external=True)

        r = resend.Emails.send({
            "from": "Job Matcher <onboarding@resend.dev>",
            "to": email,
            "subject": "Verify your email.",
            "html": f"""
                <h1>Hello from Job Matcher!</h1>
                <p>Follow this link to verify your email</p>
                <a href="{verification_url}">Verify Email</a>"""
            })

        print(r)

        flash("Verification link sent. Check your inbox.", "success")

        return redirect("/login")

    else:
        return render_template("register.html")

@app.route("/verify_email_registration/<token>")
def verify_email_registration(token):
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
        try:
            c.execute("DELETE FROM users WHERE user_id = ?", (session["user_id"], ))
        except:
            pass
        conn.commit()
        conn.close()

        session.clear()

        flash("Link expired or invalid.", "error")

        return redirect("/register")

@app.route("/learn_more")
def learn_more():
    return render_template("learn_more.html")

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")

        conn = connect_database("users.db")
        c = conn.cursor()

        if not c.execute("SELECT * FROM users WHERE email = ?", (email, )).fetchone():
            flash("This email is not linked to any existing account.", "error")
            conn.close()
            return redirect("/forgot_password")

        conn.close()

        # Creating a safe token 
        token = serializer.dumps(email, salt="reset-password")

        # Verification link that we'll put in an email
        verification_link = url_for("verify_email_password", token=token, _external=True)

        r = resend.Emails.send(
            {
                "from": "Job Matcher <onboarding@resend.dev>",
                "to": email, 
                "subject": "Reset password",
                "html": f"""
                    <h1>Hello from Job Matcher!</h1>
                    <p>This is an email to reset your password. If it weren't you, who wanted to do that, please ignore this email.</p>
                    <p>If it was you, please follow this link: <a href="{verification_link}">Reset Password</a></p>"""
            }
        )

        print(r)

        flash("Verification link sent. Please check your inbox.", "success")
        return redirect("/forgot_password")

    else:
        return render_template("forgot_password.html")


@app.route("/verify_email/<token>")
def verify_email_password(token):
    try: 
        email = serializer.loads(
            token, 
            salt="reset-password",
            max_age=3600
        )

        session["email"] = email

        return redirect("/reset_password")
    except:
        flash("Link expired or invalid.", "error")
        return redirect("/forgot_password")

@app.route("/reset_password", methods=["POST", "GET"])
def reset_password():
    if request.method == "POST":
        if "email" in session:
            password = request.form.get("password")
            confirmation = request.form.get("confirmation")
            is_valid = password_is_valid(password, confirmation)

            if is_valid != True:
                flash(is_valid, "error")
                return redirect("/reset_password")

            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

            conn = connect_database("users.db")
            c = conn.cursor()

            c.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, session["email"]))
            conn.commit()
            conn.close()

            del session["email"]

            flash("You have successfully changed your password!", "success")
            return redirect("/")

        else:
            flash("Unauthorized. Please use the link in the email.", "error")
            return redirect("/forgot_password")

    else:
        return render_template("reset_password.html")