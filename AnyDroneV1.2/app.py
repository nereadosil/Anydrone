from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATABASE = "database/anydrone.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (user_name, user_email_address, user_password) VALUES (?, ?, ?)",
                       (name, email, hashed_password))
        conn.commit()
        conn.close()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_email_address = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["user_password"], password):
            session["user_id"] = user["user_id"]
            session["name"] = user["user_name"]
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials", "danger")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drones WHERE owner_id = ?", (session["user_id"],))
    drones = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", name=session["name"], drones=drones)

@app.route("/add_drone", methods=["GET", "POST"])
def add_drone():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        model = request.form["model"]
        manufacturer = request.form["manufacturer"]
        camera_quality = request.form["camera_quality"]
        max_load = request.form["max_load"]
        flight_time = request.form["flight_time"]

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO drones (owner_id, model, manufacturer, camera_quality, max_load, flight_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session["user_id"], model, manufacturer, camera_quality, max_load, flight_time))
            
            conn.commit()  # Ensure the transaction is committed
            flash("Drone added successfully!", "success")
        except sqlite3.Error as e:
            flash(f"Error adding drone: {e}", "danger")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for("dashboard"))

    return render_template("add_drone.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out.", "info")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
