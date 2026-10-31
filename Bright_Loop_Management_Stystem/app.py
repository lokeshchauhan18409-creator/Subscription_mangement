
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import re
import sys
import getpass

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY", "brightloop-development-key-change-before-deployment"
)

DATABASE = os.path.join(app.root_path, "database.db")


# DATABASE CONNECTION
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# CREATE DATABASE TABLE
def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'customer'
        )
    """)

    conn.commit()
    conn.close()


# HOME PAGE
@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# SIGNUP PAGE
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Please fill all required fields.")
            return redirect(url_for("signup"))

        # PASSWORD VALIDATION
        if len(password) <= 8:
            flash("Password must be more than 8 characters.")
            return redirect(url_for("signup"))

        if not re.search(r"[A-Z]", password):
            flash("Password needs an uppercase letter.")
            return redirect(url_for("signup"))

        if not re.search(r"[a-z]", password):
            flash("Password needs a lowercase letter.")
            return redirect(url_for("signup"))

        if not re.search(r"[^A-Za-z0-9]", password):
            flash("Password needs a special character.")
            return redirect(url_for("signup"))

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password)

        conn = get_db()

        try:
            conn.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (?, ?, ?, ?)
            """, (name, email, hashed_password, "customer"))

            conn.commit()

            flash("Account created successfully! Please login.")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("This email is already registered.")
            return redirect(url_for("signup"))

        finally:
            conn.close()

    return render_template("signup.html")


# LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db()

        user = conn.execute("""
            SELECT * FROM users WHERE email = ?
        """, (email,)).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session.clear()

            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")
        return redirect(url_for("login"))

    return render_template("login.html")



@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    role = session.get("role")

    if role == "admin":
        return render_template("admin_dashboard.html")

    elif role == "staff":
        return render_template("staff_dashboard.html")

    elif role == "customer":
        return render_template("customer_dashboard.html")

    return redirect(url_for("logout"))


# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# CREATE FIRST ADMIN ACCOUNT
def create_admin_account():

    print("\n--- Brightloop Admin Setup ---")

    name = input("Enter admin name: ").strip()
    email = input("Enter admin email: ").strip().lower()

    password = getpass.getpass("Enter admin password: ")
    confirm = getpass.getpass("Confirm password: ")

    if not name or not email:
        print("Name and email are required.")
        return

    if len(password) <= 8:
        print("Password must be more than 8 characters.")
        return

    if not re.search(r"[A-Z]", password):
        print("Add an uppercase letter.")
        return

    if not re.search(r"[a-z]", password):
        print("Add a lowercase letter.")
        return

    if not re.search(r"[^A-Za-z0-9]", password):
        print("Add a special character.")
        return

    if password != confirm:
        print("Passwords do not match.")
        return

    conn = get_db()

    try:
        conn.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            generate_password_hash(password),
            "admin"
        ))

        conn.commit()
        print("\nAdmin account created successfully!")

    except sqlite3.IntegrityError:
        print("\nThis email is already registered.")

    finally:
        conn.close()

# CREATE FIRST ADMIN ACCOUNT
def create_admin_account():

    print("\n--- Brightloop Admin Setup ---")

    name = input("Enter admin name: ").strip()
    email = input("Enter admin email: ").strip().lower()

    password = getpass.getpass("Enter admin password: ")
    confirm = getpass.getpass("Confirm password: ")

    if not name or not email:
        print("Name and email are required.")
        return

    if len(password) <= 8:
        print("Password must be more than 8 characters.")
        return

    if not re.search(r"[A-Z]", password):
        print("Add an uppercase letter.")
        return

    if not re.search(r"[a-z]", password):
        print("Add a lowercase letter.")
        return

    if not re.search(r"[^A-Za-z0-9]", password):
        print("Add a special character.")
        return

    if password != confirm:
        print("Passwords do not match.")
        return

    conn = get_db()

    try:
        conn.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            generate_password_hash(password),
            "admin"
        ))

        conn.commit()
        print("\nAdmin account created successfully!")

    except sqlite3.IntegrityError:
        print("\nThis email is already registered.")

    finally:
        conn.close()


# APPLICATION START
if __name__ == "__main__":

    init_db()

    if len(sys.argv) > 1 and sys.argv[1] == "create-admin":
        create_admin_account()
    else:
        app.run(debug=True)