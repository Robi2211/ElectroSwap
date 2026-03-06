"""Authentication blueprint – register, login, logout, profile."""

from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from bson import ObjectId
import bcrypt

from app import db
from app.models import User

auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        # Validation
        errors = []
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if not email or "@" not in email:
            errors.append("A valid email is required.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if db.users.find_one({"email": email}):
            errors.append("An account with that email already exists.")
        if db.users.find_one({"username": username}):
            errors.append("That username is taken.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("register.html", username=username, email=email)

        pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user_doc = {
            "username": username,
            "email": email,
            "password_hash": pw_hash,
            "role": "customer",
            "address": {"street": "", "city": "", "zip_code": "", "country": ""},
            "created_at": datetime.now(timezone.utc),
        }
        result = db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        login_user(User(user_doc))
        flash("Welcome to ElectroSwap!", "success")
        return redirect(url_for("main.index"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user_doc = db.users.find_one({"email": email})
        if user_doc and bcrypt.checkpw(password.encode("utf-8"), user_doc["password_hash"].encode("utf-8")):
            login_user(User(user_doc), remember=request.form.get("remember"))
            flash("Welcome back!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))

        flash("Invalid email or password.", "error")
        return render_template("login.html", email=email)

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """User profile – view and update address."""
    if request.method == "POST":
        street = request.form.get("street", "").strip()
        city = request.form.get("city", "").strip()
        zip_code = request.form.get("zip_code", "").strip()
        country = request.form.get("country", "").strip()

        db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {"address": {"street": street, "city": city, "zip_code": zip_code, "country": country}}},
        )
        flash("Address updated.", "success")
        return redirect(url_for("auth.profile"))

    user_doc = db.users.find_one({"_id": ObjectId(current_user.id)})
    return render_template("profile.html", user=user_doc)
