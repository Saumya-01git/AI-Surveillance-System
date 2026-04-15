from flask import Flask, render_template, request, redirect, session
import threading
from detect import run_detection
from db import get_connection

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid Credentials")

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect("/")

    db = get_connection()
    cursor = db.cursor()

    # Total Alerts
    cursor.execute("SELECT COUNT(*) FROM alerts")
    total = cursor.fetchone()[0]

    # Pending Alerts
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE status='Pending'")
    pending = cursor.fetchone()[0]

    # HIGH Threat Alerts
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE threat_level='HIGH'")
    high_threats = cursor.fetchone()[0]

    # MEDIUM Threat Alerts
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE threat_level='MEDIUM'")
    medium_threats = cursor.fetchone()[0]

    cursor.close()
    db.close()

    return render_template(
        "dashboard.html",
        total=total,
        pending=pending,
        high_threats=high_threats,
        medium_threats=medium_threats
    )


# ---------------- START DETECTION ----------------
@app.route("/start", methods=["POST"])
def start():
    environment = request.form.get("environment")
    video = request.form.get("video")

    thread = threading.Thread(
        target=run_detection,
        args=(video, environment)
    )
    thread.start()

    return redirect("/alerts")


# ---------------- VIEW ALERTS ----------------
@app.route("/alerts")
def alerts():
    if "admin" not in session:
        return redirect("/")

    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
        SELECT a.alert_id, a.timestamp, 
               c.location, 
               a.track_id, 
               e.event_name, 
               a.risk_score, 
               a.threat_level,
               a.status
        FROM alerts a
        JOIN cameras c ON a.camera_id = c.camera_id
        JOIN events e ON a.event_id = e.event_id
        ORDER BY a.timestamp DESC
    """)

    data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("alerts.html", alerts=data)


# ---------------- UPDATE STATUS ----------------
@app.route("/update/<int:alert_id>/<string:new_status>")
def update_status(alert_id, new_status):
    db = get_connection()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE alerts SET status=%s WHERE alert_id=%s",
        (new_status, alert_id)
    )
    db.commit()

    cursor.close()
    db.close()

    return redirect("/alerts")


# ---------------- ANALYTICS ----------------
@app.route("/analytics")
def analytics():
    if "admin" not in session:
        return redirect("/")

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    # 1️⃣ Most Dangerous Locations
    cursor.execute("""
        SELECT c.location, COUNT(*) as total
        FROM alerts a
        JOIN cameras c ON a.camera_id = c.camera_id
        GROUP BY c.location
        ORDER BY total DESC
    """)
    location_data = cursor.fetchall()

    # 2️⃣ Most Frequent Events
    cursor.execute("""
        SELECT e.event_name, COUNT(*) as total
        FROM alerts a
        JOIN events e ON a.event_id = e.event_id
        GROUP BY e.event_name
        ORDER BY total DESC
    """)
    event_data = cursor.fetchall()

    # 3️⃣ Top Risk Persons
    cursor.execute("""
        SELECT track_id, MAX(risk_score) as max_risk
        FROM alerts
        GROUP BY track_id
        ORDER BY max_risk DESC
    """)
    person_data = cursor.fetchall()

    # 4️⃣ Threat Level Distribution
    cursor.execute("""
        SELECT threat_level, COUNT(*) as total
        FROM alerts
        GROUP BY threat_level
    """)
    threat_data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "analytics.html",
        location_data=location_data,
        event_data=event_data,
        person_data=person_data,
        threat_data=threat_data
    )


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)