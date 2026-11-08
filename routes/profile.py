from flask import Blueprint, render_template, request, redirect, session

profile = Blueprint("profile", __name__)

@profile.route("/settings")
def settings():
    return render_template("settings.html", show_nav=True)

@profile.route("/logout", methods=["POST"])
def logout():
    button_value = request.form.get("logout_answer")

    if button_value == "no_log_out":
        return redirect("/settings")

    del session["user_id"]
    
    return redirect("/landing_page")