from flask import Flask, render_template, request, redirect, session
from functools import wraps
from dotenv import load_dotenv
import os

from routes.auth import auth
from routes.jobs import jobs
from routes.profile import profile

from extensions import oauth

load_dotenv()

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

app.register_blueprint(auth)
#app.register_blueprint(jobs)
#app.register_blueprint(profile)

oauth.init_app(app)


@app.route("/")
@login_required
def index():
    return render_template("index.html", show_nav=True)

@app.route("/landing_page")
def landing_page():
    return render_template("landing_page.html")

@app.route("/about")
def about():
    return render_template("learn_more.html", show_nav=True)

@app.route("/jobs", methods=["POST", "GET"])
def jobs():
    if request.method == "POST":
        pass
    else:
        return render_template("find_jobs.html", show_nav=True)

@app.route("/saved_jobs")
def saved_jobs():
    # TODO
    return redirect("/landing_page")

