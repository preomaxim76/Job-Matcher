from flask import Flask, render_template, request, redirect, session, flash
from functools import wraps
from dotenv import load_dotenv
import os

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

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        pass
    
    else:
        return render_template("login.html", show_nav=False)
    