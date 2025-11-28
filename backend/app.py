from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_db_connection, init_db, is_db_initialized
import mysql.connector

app = Flask(__name__)
CORS(app)


def ensure_db_initialized_on_startup():
    """Optionally initialize the database schema on first run.

    This checks whether the core tables exist. If they do not, it will run the
    **destructive** ``init_db()`` function from ``db.py``, which executes
    ``backend/schema.sql`` (including ``DROP TABLE IF EXISTS ...``).

    Normal runs where the schema already exists will **not** modify data.
    """

    try:
        if is_db_initialized():
            app.logger.info(
                "Database already initialized; starting without changes.")
            return
    except Exception as exc:  # Defensive: don't block startup on the check itself
        app.logger.warning(f"Could not verify database initialization: {exc}")

    app.logger.warning(
        "Database appears uninitialized or check failed. "
        "Running destructive init_db() using backend/schema.sql."
    )
    init_db()


def parse_json(required_fields=None):
    """Safely parse JSON body and validate required fields.

    Returns (data, error_response). If error_response is not None, return it
    directly from the view.
    """
    if not request.is_json:
        return None, (jsonify({"error": "Request content type must be application/json"}), 400)

    data = request.get_json(silent=True)
    if data is None:
        return None, (jsonify({"error": "Invalid JSON body"}), 400)

    if required_fields:
        missing = [f for f in required_fields if f not in data]
        if missing:
            return None, (jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400)

    return data, None


def get_connection_or_response():
    """Get a DB connection or a standardized error response."""
    conn = get_db_connection()
    if not conn:
        return None, (jsonify({"error": "Database connection failed"}), 500)
    return conn, None


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200


@app.route('/api/query', methods=['POST'])
def execute_query():
    """Execute a read-only SQL query.

    For security, this endpoint only allows SELECT statements.
    """
    data, error_response = parse_json(required_fields=['query'])
    if error_response:
        return error_response

    query = data['query']
    if not query or not query.strip():
        return jsonify({"error": "Query cannot be empty"}), 400

    # Dev Mode: Allow all queries (INSERT, UPDATE, DELETE, DROP, etc.)
    # WARNING: This is dangerous in production!

    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query)

        # If it's a SELECT query, return results
        if query.strip().upper().startswith("SELECT") or query.strip().upper().startswith("SHOW"):
            result = cursor.fetchall()
            return jsonify(result), 200
        else:
            # For write operations, commit and return success message
            conn.commit()
            return jsonify({
                "message": "Query executed successfully",
                "rows_affected": cursor.rowcount
            }), 200

    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": str(e), "code": e.errno}), 400
    finally:
        cursor.close()
        conn.close()


# --- CRUD Endpoints for Person ---
@app.route('/api/persons', methods=['GET', 'POST'])
def manage_persons():
    if request.method == 'GET':
        conn, error_response = get_connection_or_response()
        if error_response:
            return error_response

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM Person")
            persons = cursor.fetchall()
            return jsonify(persons), 200
        except mysql.connector.Error as e:
            return jsonify({"error": str(e)}), 400
        finally:
            cursor.close()
            conn.close()

    # POST
    data, error_response = parse_json(required_fields=['personal_id', 'name'])
    if error_response:
        return error_response

    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        sql = (
            "INSERT INTO Person (personal_id, name, age, gender, date_of_birth, supervisor_id) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        val = (
            data['personal_id'],
            data['name'],
            data.get('age'),
            data.get('gender'),
            data.get('date_of_birth'),
            data.get('supervisor_id'),
        )
        cursor.execute(sql, val)
        conn.commit()
        return jsonify({"message": "Person created"}), 201
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# --- Profile Endpoints ---
@app.route('/api/profiles', methods=['GET', 'POST'])
def manage_profiles():
    if request.method == 'GET':
        conn, error_response = get_connection_or_response()
        if error_response:
            return error_response

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT p.*, pr.job_role, pr.status
                FROM Profile pr
                JOIN Person p ON pr.personal_id = p.personal_id
                """
            )
            profiles = cursor.fetchall()
            return jsonify(profiles), 200
        except mysql.connector.Error as e:
            return jsonify({"error": str(e)}), 400
        finally:
            cursor.close()
            conn.close()

    # POST
    data, error_response = parse_json(
        required_fields=['personal_id', 'job_role'])
    if error_response:
        return error_response

    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        sql = "INSERT INTO Profile (personal_id, job_role, status) VALUES (%s, %s, %s)"
        val = (data['personal_id'], data['job_role'],
               data.get('status', 'Current'))
        cursor.execute(sql, val)
        conn.commit()
        return jsonify({"message": "Profile created"}), 201
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# --- School Endpoints ---
@app.route('/api/schools', methods=['GET', 'POST'])
def manage_schools():
    if request.method == 'GET':
        conn, error_response = get_connection_or_response()
        if error_response:
            return error_response

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM School")
            schools = cursor.fetchall()
            return jsonify(schools), 200
        except mysql.connector.Error as e:
            return jsonify({"error": str(e)}), 400
        finally:
            cursor.close()
            conn.close()

    # POST
    data, error_response = parse_json(
        required_fields=['school_name', 'department'])
    if error_response:
        return error_response

    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        sql = "INSERT INTO School (school_name, department, faculty) VALUES (%s, %s, %s)"
        val = (data['school_name'], data['department'], data.get('faculty'))
        cursor.execute(sql, val)
        conn.commit()
        return jsonify({"message": "School created"}), 201
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# --- Location Endpoints ---
@app.route('/api/locations', methods=['GET', 'POST'])
def manage_locations():
    if request.method == 'GET':
        conn, error_response = get_connection_or_response()
        if error_response:
            return error_response

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT l.*, s.department, s.faculty
                FROM Location l
                LEFT JOIN School s ON l.school_name = s.school_name
                """
            )
            locations = cursor.fetchall()
            return jsonify(locations), 200
        except mysql.connector.Error as e:
            return jsonify({"error": str(e)}), 400
        finally:
            cursor.close()
            conn.close()

    # POST (all fields optional except none are explicitly NOT NULL in schema
    data, error_response = parse_json()
    if error_response:
        return error_response

    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        sql = (
            "INSERT INTO Location (room, floor, building, campus, school_name) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        val = (
            data.get('room'),
            data.get('floor'),
            data.get('building'),
            data.get('campus'),
            data.get('school_name'),
        )
        cursor.execute(sql, val)
        conn.commit()
        return jsonify({"message": "Location created"}), 201
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# --- Activity Endpoints ---
@app.route('/api/activities', methods=['GET', 'POST'])
def manage_activities():
    if request.method == 'GET':
        conn, error_response = get_connection_or_response()
        if error_response:
            return error_response

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT a.*, p.name AS organiser_name
                FROM Activity a
                JOIN Person p ON a.organiser_id = p.personal_id
                """
            )
            activities = cursor.fetchall()
            return jsonify(activities), 200
        except mysql.connector.Error as e:
            return jsonify({"error": str(e)}), 400
        finally:
            cursor.close()
            conn.close()

    # POST
    data, error_response = parse_json(
        required_fields=['activity_id', 'organiser_id'])
    if error_response:
        return error_response

    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        sql = "INSERT INTO Activity (activity_id, type, time, organiser_id) VALUES (%s, %s, %s, %s)"
        val = (
            data['activity_id'],
            data.get('type'),
            data.get('time'),
            data['organiser_id'],
        )
        cursor.execute(sql, val)
        conn.commit()
        return jsonify({"message": "Activity created"}), 201
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# --- Maintenance Endpoints ---
@app.route('/api/maintenance', methods=['GET', 'POST'])
def manage_maintenance():
    if request.method == 'GET':
        conn, error_response = get_connection_or_response()
        if error_response:
            return error_response

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT m.*, l.building, l.room, l.campus
                FROM Maintenance m
                JOIN Location l ON m.location_id = l.location_id
                """
            )
            maintenance = cursor.fetchall()
            return jsonify(maintenance), 200
        except mysql.connector.Error as e:
            return jsonify({"error": str(e)}), 400
        finally:
            cursor.close()
            conn.close()

    # POST
    data, error_response = parse_json(required_fields=['type', 'location_id'])
    if error_response:
        return error_response

    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        sql = "INSERT INTO Maintenance (type, frequency, location_id) VALUES (%s, %s, %s)"
        val = (data['type'], data.get('frequency'), data['location_id'])
        cursor.execute(sql, val)
        conn.commit()
        return jsonify({"message": "Maintenance task created"}), 201
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# --- Many-to-Many Relationship Endpoints ---

# Participation (Person-Activity)
@app.route('/api/participations', methods=['GET', 'POST'])
def manage_participations():
    if request.method == 'GET':
        conn, error_response = get_connection_or_response()
        if error_response:
            return error_response

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT p.personal_id, per.name AS person_name,
                       a.activity_id, a.type AS activity_type
                FROM Participation p
                JOIN Person per ON p.personal_id = per.personal_id
                JOIN Activity a ON p.activity_id = a.activity_id
                """
            )
            participations = cursor.fetchall()
            return jsonify(participations), 200
        except mysql.connector.Error as e:
            return jsonify({"error": str(e)}), 400
        finally:
            cursor.close()
            conn.close()

    # POST
    data, error_response = parse_json(
        required_fields=['personal_id', 'activity_id'])
    if error_response:
        return error_response

    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        sql = "INSERT INTO Participation (personal_id, activity_id) VALUES (%s, %s)"
        val = (data['personal_id'], data['activity_id'])
        cursor.execute(sql, val)
        conn.commit()
        return jsonify({"message": "Participation added"}), 201
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# Affiliation (Person-School)
@app.route('/api/affiliations', methods=['GET', 'POST'])
def manage_affiliations():
    if request.method == 'GET':
        conn, error_response = get_connection_or_response()
        if error_response:
            return error_response

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT a.personal_id, p.name AS person_name,
                       s.school_name, s.department
                FROM Affiliation a
                JOIN Person p ON a.personal_id = p.personal_id
                JOIN School s ON a.school_name = s.school_name
                """
            )
            affiliations = cursor.fetchall()
            return jsonify(affiliations), 200
        except mysql.connector.Error as e:
            return jsonify({"error": str(e)}), 400
        finally:
            cursor.close()
            conn.close()

    # POST
    data, error_response = parse_json(
        required_fields=['personal_id', 'school_name'])
    if error_response:
        return error_response

    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        sql = "INSERT INTO Affiliation (personal_id, school_name) VALUES (%s, %s)"
        val = (data['personal_id'], data['school_name'])
        cursor.execute(sql, val)
        conn.commit()
        return jsonify({"message": "Affiliation added"}), 201
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# --- Advanced Report Endpoints ---

# Report 1: Maintenance by Location and Type
@app.route('/api/reports/maintenance-summary', methods=['GET'])
def maintenance_report():
    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        query = (
            """
            SELECT m.type, l.building, l.campus, COUNT(*) AS count
            FROM Maintenance m
            JOIN Location l ON m.location_id = l.location_id
            GROUP BY m.type, l.building, l.campus
            ORDER BY count DESC
            """
        )
        cursor.execute(query)
        report = cursor.fetchall()
        return jsonify(report), 200
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# Report 2: People by Job Role and Status
@app.route('/api/reports/people-summary', methods=['GET'])
def people_report():
    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        query = (
            """
            SELECT pr.job_role, pr.status, COUNT(*) AS count
            FROM Profile pr
            GROUP BY pr.job_role, pr.status
            ORDER BY pr.job_role, count DESC
            """
        )
        cursor.execute(query)
        report = cursor.fetchall()
        return jsonify(report), 200
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# Report 3: Activities by Type and Organiser
@app.route('/api/reports/activities-summary', methods=['GET'])
def activities_report():
    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        query = (
            """
            SELECT a.type, p.name AS organiser_name, COUNT(*) AS activity_count
            FROM Activity a
            JOIN Person p ON a.organiser_id = p.personal_id
            GROUP BY a.type, p.name
            ORDER BY activity_count DESC
            """
        )
        cursor.execute(query)
        report = cursor.fetchall()
        return jsonify(report), 200
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# Report 4: School Department Statistics
@app.route('/api/reports/school-stats', methods=['GET'])
def school_stats():
    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        query = (
            """
            SELECT s.school_name, s.department,
                   COUNT(DISTINCT a.personal_id) AS affiliated_people,
                   COUNT(DISTINCT l.location_id) AS locations_count
            FROM School s
            LEFT JOIN Affiliation a ON s.school_name = a.school_name
            LEFT JOIN Location l ON s.school_name = l.school_name
            GROUP BY s.school_name, s.department
            """
        )
        cursor.execute(query)
        report = cursor.fetchall()
        return jsonify(report), 200
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# Report 5: Maintenance Frequency Analysis
@app.route('/api/reports/maintenance-frequency', methods=['GET'])
def maintenance_frequency():
    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        query = (
            """
            SELECT frequency, type, COUNT(*) AS task_count
            FROM Maintenance
            GROUP BY frequency, type
            ORDER BY frequency, task_count DESC
            """
        )
        cursor.execute(query)
        report = cursor.fetchall()
        return jsonify(report), 200
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    # Optionally initialize the DB on first run. This will only call the
    # destructive init_db() if the core tables are missing.
    ensure_db_initialized_on_startup()
    app.run(debug=True, host='0.0.0.0', port=5050)
