from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_db_connection, init_db
import mysql.connector

app = Flask(__name__)
CORS(app)

# Initialize DB on start (optional, or run db.py manually)
# init_db()


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200


@app.route('/api/query', methods=['POST'])
def execute_query():
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query)
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
            return jsonify(result), 200
        else:
            conn.commit()
            return jsonify({"message": "Query executed successfully", "rows_affected": cursor.rowcount}), 200
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# --- CRUD Endpoints for Person ---


@app.route('/api/persons', methods=['GET', 'POST'])
def manage_persons():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor(dictionary=True)

    if request.method == 'GET':
        cursor.execute("SELECT * FROM Person")
        persons = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(persons), 200

    elif request.method == 'POST':
        data = request.json
        try:
            sql = "INSERT INTO Person (personal_id, name, age, gender, date_of_birth, supervisor_id) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (data['personal_id'], data['name'], data.get('age'), data.get(
                'gender'), data.get('date_of_birth'), data.get('supervisor_id'))
            cursor.execute(sql, val)
            conn.commit()
            return jsonify({"message": "Person created"}), 201
        except mysql.connector.Error as e:
            return jsonify({"error": str(e)}), 400
        finally:
            cursor.close()
            conn.close()

# --- Report Generation Endpoint ---


@app.route('/api/reports/maintenance-summary', methods=['GET'])
def maintenance_report():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor(dictionary=True)

    # Example report: Count of maintenance activities by type and location
    query = """
    SELECT m.type, l.building, COUNT(*) as count
    FROM Maintenance m
    JOIN Location l ON m.location_id = l.location_id
    GROUP BY m.type, l.building
    """
    cursor.execute(query)
    report = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(report), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
