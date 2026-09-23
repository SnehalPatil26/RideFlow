import os
import sqlite3
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.path.join(BASE_DIR, "database", "rideflow.db")


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


@app.route("/")
def home():
    return send_from_directory(
        os.path.dirname(__file__),
        "index.html"
    )


@app.route("/api/summary")
def summary():
    conn = get_connection()

    total = conn.execute(
        "SELECT COUNT(*) AS count FROM bookings"
    ).fetchone()["count"]

    successful = conn.execute(
        "SELECT COUNT(*) AS count FROM bookings WHERE is_successful = 1"
    ).fetchone()["count"]

    revenue = conn.execute(
        "SELECT COALESCE(SUM(booking_value), 0) AS total FROM bookings"
    ).fetchone()["total"]

    avg_distance = conn.execute(
        "SELECT COALESCE(AVG(ride_distance), 0) AS avg FROM bookings"
    ).fetchone()["avg"]

    conn.close()

    success_rate = (successful / total * 100) if total else 0

    return jsonify({
        "total_rides": total,
        "successful_rides": successful,
        "success_rate": round(success_rate, 2),
        "total_revenue": round(revenue, 2),
        "average_distance": round(avg_distance, 2)
    })


@app.route("/api/vehicles")
def vehicles():
    conn = get_connection()

    rows = conn.execute("""
        SELECT
            vehicle_type,
            COUNT(*) AS rides,
            ROUND(AVG(booking_value), 2) AS avg_booking_value,
            ROUND(AVG(ride_distance), 2) AS avg_distance
        FROM bookings
        GROUP BY vehicle_type
        ORDER BY rides DESC
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/api/payments")
def payments():
    conn = get_connection()

    rows = conn.execute("""
        SELECT
            payment_method,
            COUNT(*) AS rides,
            ROUND(SUM(booking_value), 2) AS revenue
        FROM bookings
        GROUP BY payment_method
        ORDER BY rides DESC
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/api/status")
def status():
    conn = get_connection()

    rows = conn.execute("""
        SELECT
            booking_status,
            COUNT(*) AS count
        FROM bookings
        GROUP BY booking_status
        ORDER BY count DESC
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/api/monthly")
def monthly():
    conn = get_connection()

    rows = conn.execute("""
        SELECT
            year,
            month,
            month_name,
            COUNT(*) AS rides,
            ROUND(SUM(booking_value), 2) AS revenue
        FROM bookings
        GROUP BY year, month, month_name
        ORDER BY year, month
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])

@app.route("/api/locations")
def locations():
    conn = get_connection()

    pickup_rows = conn.execute("""
        SELECT
            pickup_location AS location,
            COUNT(*) AS rides
        FROM bookings
        GROUP BY pickup_location
        ORDER BY rides DESC
        LIMIT 10
    """).fetchall()

    drop_rows = conn.execute("""
        SELECT
            drop_location AS location,
            COUNT(*) AS rides
        FROM bookings
        GROUP BY drop_location
        ORDER BY rides DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    return jsonify({
        "pickup": [dict(row) for row in pickup_rows],
        "drop": [dict(row) for row in drop_rows]
    })

if __name__ == "__main__":
    print("=" * 60)
    print("          RIDEFLOW ANALYTICS API")
    print("=" * 60)
    print("Database:", DATABASE)
    print("API: http://127.0.0.1:5000")
    print("=" * 60)

    import os

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )