from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash

# ✅ Flask App Initialization
app = Flask(__name__)
app.secret_key = "your_secret_key"

# ✅ Database File Path
DB_FILE = "app.db"


# ✅ Initialize Database
def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # ✅ Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            date_of_birth TEXT,
            gender TEXT,
            email TEXT UNIQUE NOT NULL,
            phone_number TEXT,
            aadhaar_number TEXT,
            pan_number TEXT,
            bank_account_number TEXT,
            current_address TEXT,
            permanent_address TEXT,
            occupation TEXT,
            monthly_income REAL,
            loan_purpose TEXT,
            consent INTEGER,
            password TEXT NOT NULL
        )
    ''')
    
    # ✅ Loans Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            application_date TEXT DEFAULT CURRENT_TIMESTAMP,
            amount REAL NOT NULL,
            duration INTEGER NOT NULL,
            purpose TEXT,
            employment_type TEXT,
            annual_income REAL,
            credit_score INTEGER,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()


initialize_database()


# ✅ Database Connection Helper
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# ✅ Home Route
@app.route("/")
def home():
    if "user_id" in session:
        user_type = session.get("user_type", "User")
        return render_template("index.html", user_type=user_type)
    return render_template("index.html")


# ✅ Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html')
    return redirect(url_for('login'))


# ✅ Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_type = request.form.get("user_type")
        login_credential = request.form.get("login_credential")
        password = request.form.get("password")

        # Validate email or phone number
        if re.match(r"[^@]+@[^@]+\.[^@]+", login_credential):
            field = "email"
        elif re.match(r"^\d{10}$", login_credential):
            field = "phone_number"
        else:
            flash("Invalid email or phone number format!", "error")
            return render_template("login.html")

        conn = get_db_connection()
        user = conn.execute(
            f"SELECT * FROM users WHERE {field} = ?",
            (login_credential,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            if user_type.lower() == "admin" and user["email"] != "admin@example.com":
                flash("You do not have admin privileges!", "error")
                return render_template("login.html")
            
            # Set session
            session["user_id"] = user["id"]
            session["user_type"] = user_type
            session["email"] = user["email"]
            session["user_logged_in"] = True

            flash(f"{user_type} Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials. Please try again.", "error")

    return render_template("login.html")


# ✅ Register Route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form = request.form

        # Fetching data from the form
        full_name = form.get("full_name")
        date_of_birth = form.get("date_of_birth")
        gender = form.get("gender")
        email = form.get("email")
        phone_number = form.get("phone_number")
        aadhaar_number = form.get("aadhaar_number")
        pan_number = form.get("pan_number")
        bank_account_number = form.get("bank_account_number")
        current_address = form.get("current_address")
        permanent_address = form.get("permanent_address") if form.get("same_address") != "on" else current_address
        occupation = form.get("occupation")
        monthly_income = form.get("monthly_income")
        loan_purpose = form.get("loan_purpose")
        consent = 1 if form.get("consent") == "on" else 0
        password = form.get("password")
        confirm_password = form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return render_template("register.html")

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO users (full_name, date_of_birth, gender, email, phone_number,
                aadhaar_number, pan_number, bank_account_number, current_address, permanent_address,
                occupation, monthly_income, loan_purpose, consent, password)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (full_name, date_of_birth, gender, email, phone_number, aadhaar_number, pan_number,
                  bank_account_number, current_address, permanent_address, occupation,
                  monthly_income, loan_purpose, consent, hashed_password))
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already exists!", "error")
        finally:
            conn.close()

    return render_template("register.html")


# ✅ Loan Application Route
@app.route("/loan_application", methods=["GET", "POST"])
def loan_application():
    if "user_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        form = request.form
        loan_amount = form.get("loan_amount")
        loan_duration = form.get("loan_duration")
        loan_purpose = form.get("loan_purpose")
        employment_type = form.get("employment_type")
        annual_income = form.get("annual_income")

        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO loans (user_id, amount, duration, purpose, employment_type, annual_income, status)
                VALUES (?, ?, ?, ?, ?, ?, 'Pending')
            ''', (session["user_id"], loan_amount, loan_duration, loan_purpose, employment_type, annual_income))
            conn.commit()
            flash("Loan application submitted successfully!", "success")
            return redirect(url_for("loan_status"))
        finally:
            conn.close()

    return render_template("loan_application.html")

@app.route('/previous_loans')
def previous_loans():
    if "user_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login"))
    # Add logic for previous loans here
    return render_template("previous_loans.html")

# Custom INR Filter
@app.template_filter('inr')
def inr_format(value):
    try:
        return f"₹{float(value):,.2f}"
    except (ValueError, TypeError):
        return value


# ✅ Loan Status Route
@app.route("/loan_status")
def loan_status():
    if "user_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    loan = conn.execute('''
        SELECT * FROM loans WHERE user_id = ? ORDER BY application_date DESC LIMIT 1
    ''', (session["user_id"],)).fetchone()
    conn.close()

    return render_template("loan_status.html", loan=loan)


# ✅ Run Application
if __name__ == "__main__":
    app.run(debug=True)
