from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


# ---------------- DATABASE ----------------

def create_database():
    conn = sqlite3.connect("waste.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            waste TEXT,
            location TEXT,
            date TEXT,
            time TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    conn.commit()
    conn.close()


# ---------------- HOME ----------------

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        name = request.form.get("name")
        waste = request.form.get("waste")
        location = request.form.get("location")
        date = request.form.get("date")
        time = request.form.get("time")

        conn = sqlite3.connect("waste.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO requests
            (name, waste, location, date, time, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, waste, location, date, time, "Pending"))

        conn.commit()
        conn.close()

        return render_template(
            "home.html",
            message="Pickup Request Submitted Successfully!"
        )

    return render_template("home.html")


# ---------------- ADMIN + SEARCH/FILTER ----------------

@app.route("/admin")
def admin():

    search = request.args.get("search", "")
    status = request.args.get("status", "")
    waste = request.args.get("waste", "")

    conn = sqlite3.connect("waste.db")
    cursor = conn.cursor()

    query = "SELECT * FROM requests WHERE 1=1"
    values = []

    if search:
        query += """
            AND (
                name LIKE ?
                OR location LIKE ?
                OR waste LIKE ?
            )
        """
        search_value = "%" + search + "%"
        values.extend([search_value, search_value, search_value])

    if status:
        query += " AND status = ?"
        values.append(status)

    if waste:
        query += " AND waste = ?"
        values.append(waste)

    query += " ORDER BY id DESC"

    cursor.execute(query, values)
    requests = cursor.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        requests=requests,
        search=search,
        status=status,
        waste=waste
    )


# ---------------- UPDATE STATUS ----------------

@app.route("/update_status/<int:request_id>", methods=["POST"])
def update_status(request_id):

    conn = sqlite3.connect("waste.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE requests SET status = ? WHERE id = ?",
        ("Collected", request_id)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- STATISTICS ----------------

@app.route("/statistics")
def statistics():

    conn = sqlite3.connect("waste.db")

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM requests")
    total = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM requests WHERE status = ?",
        ("Pending",)
    )
    pending = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM requests WHERE status = ?",
        ("Collected",)
    )
    collected = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "statistics.html",
        total=total,
        pending=pending,
        collected=collected
    )


# ---------------- PICKUP HISTORY ----------------

@app.route("/history")
def history():

    conn = sqlite3.connect("waste.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM requests
        WHERE status = 'Collected'
        ORDER BY id DESC
    """)

    requests = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        requests=requests
    )


# ---------------- START APP ----------------

if __name__ == "__main__":
    create_database()
    app.run(debug=True)