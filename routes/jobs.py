from flask import Blueprint, request, render_template, redirect

jobs = Blueprint("jobs", __name__)

@jobs.route("/jobs", methods=["POST", "GET"])
def jobs_page():
    if request.method == "POST":
        pass
    else:
        return render_template("find_jobs.html", show_nav=True, show_groq=True)

@jobs.route("/saved_jobs")
def saved_jobs():
    # TODO
    return render_template("saved_jobs.html", show_nav=True, show_groq=True)

