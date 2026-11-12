from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from database.db import connect_database
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import os
import requests
from routes.auth import send_verification_email

profile = Blueprint("profile", __name__)
profile.secret_key = os.environ["SESSION_KEY"]

serializer = URLSafeTimedSerializer(
    profile.secret_key
)

@profile.route("/verify_email_change/<token>")
def verify_email_change(token):
    try:
        email = serializer.loads(
                token=token,
                salt="email-verification-change",
                max_age=3600
            )
        flash("Your email has been successfully verified.", "success")

        conn = connect_database("users.db")
        c = conn.cursor()

        c.execute("UPDATE TABLE users SET email = ? WHERE user_id = ?", (email, session["user_id"])) # Change email 
        conn.commit()
        conn.close()

        session["email"] = email

        return redirect("/settings")
    
    except SignatureExpired:
        flash("Verification link has expired!", "error")

        return redirect("/settings")

    except BadSignature:
        flash("Verification link is invalid!", "error")

        return redirect("/settings")

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

@profile.route("/change_profile_info", methods=["POST"])
def change_profile_info():
    username = request.form.get("username")
    email = request.form.get("email")
    avatar = request.files.get("avatar_photo")

    conn = connect_database("users.db")
    c = conn.cursor()

    # Change username
    if username:
        if username.isdigit() or not (2 < len(username) < 19):
            flash("Please enter a valid username!", "error")
            conn.close()
            return redirect("/settings")
        
        c.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, session["user_id"]))
        session["username"] = username
        conn.commit()

    # Change or add an avatar
    if avatar:
        print("PHOTO")
    
    # Change email
    if email:
        if not email.endswith("@gmail.com"):
            flash("Email is not valid. Please enter a valid one.", "error")
            conn.close()
            return redirect("/settings")

        # Check if that email is already in use
        if c.execute("SELECT email FROM users WHERE email = ?", (email, )).fetchall() != []:
            flash("This email is linked to an existing account.", "error")
            conn.close()
            return redirect("/settings")

        token = serializer.dumps(email, salt="email-verification-change")
                
        # Verification url with the whole route (.../verify_email_change/...)
        verification_url = url_for("profile.verify_email_change", token=token, _external=True)

        r = send_verification_email(email, verification_url)

        print(r)

    conn.close()
    print(request.files)

    flash("Your changes have been saved!", "success")
    return redirect("/settings")