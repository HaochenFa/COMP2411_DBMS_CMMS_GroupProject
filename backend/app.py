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

    # Restrict to read-only operations for safety
    if not query.strip().upper().startswith("SELECT"):
        return jsonify({"error": "Only SELECT queries are allowed via this endpoint."}), 400

    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return jsonify(result), 200
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 400
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


@app.route('/api/persons/<id>', methods=['PUT', 'DELETE'])
def manage_person_item(id):
    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response
    cursor = conn.cursor(dictionary=True)

    if request.method == 'DELETE':
        try:
            # First delete dependencies (Participation, Affiliation, Profile)
            cursor.execute(
                "DELETE FROM Participation WHERE personal_id = %s", (id,))
            cursor.execute(
                "DELETE FROM Affiliation WHERE personal_id = %s", (id,))
            cursor.execute("DELETE FROM Profile WHERE personal_id = %s", (id,))
            # Then delete Person
            cursor.execute("DELETE FROM Person WHERE personal_id = %s", (id,))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({"error": "Person not found"}), 404
            return jsonify({"message": "Person deleted"}), 200
        except mysql.connector.Error as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 400
        finally:
            cursor.close()
            conn.close()

    # PUT
    data, error_response = parse_json()
    if error_response:
        return error_response

    try:
        # Dynamic update query
        fields = []
        values = []
        if 'name' in data:
            fields.append("name = %s")
            values.append(data['name'])
        if 'age' in data:
            fields.append("age = %s")
            values.append(data['age'])
        if 'gender' in data:
            fields.append("gender = %s")
            values.append(data['gender'])
        if 'date_of_birth' in data:
            fields.append("date_of_birth = %s")
            values.append(data['date_of_birth'])
        if 'supervisor_id' in data:
            fields.append("supervisor_id = %s")
            values.append(data['supervisor_id'])

        if not fields:
            return jsonify({"error": "No fields to update"}), 400

        values.append(id)
        sql = f"UPDATE Person SET {', '.join(fields)} WHERE personal_id = %s"
        cursor.execute(sql, tuple(values))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Person not found"}), 404
        return jsonify({"message": "Person updated"}), 200
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
        # Enforce Limits
        job_role = data['job_role']
        if job_role in ['Mid-level Manager', 'Base-level Worker']:
            limit = 10 if job_role == 'Mid-level Manager' else 50
            cursor.execute(
                "SELECT COUNT(*) as count FROM Profile WHERE job_role = %s AND status = 'Current'",
                (job_role,)
            )
            count = cursor.fetchone()['count']
            if count >= limit:
                return jsonify({"error": f"Limit reached for {job_role} (Max: {limit})"}), 400

        sql = "INSERT INTO Profile (personal_id, job_role, status) VALUES (%s, %s, %s)"
        val = (data['personal_id'], job_role,
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
            # Only show legitimate schools (those with a faculty assigned)
            cursor.execute("""
                SELECT s.*, l.building, l.room
                FROM School s
                LEFT JOIN Location l ON s.hq_location_id = l.location_id
                WHERE s.faculty IS NOT NULL
            """)
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
        sql = "INSERT INTO School (school_name, department, faculty, hq_location_id) VALUES (%s, %s, %s, %s)"
        val = (data['school_name'], data['department'],
               data.get('faculty'), data.get('hq_location_id'))
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
            "INSERT INTO Location (room, floor, building, type, campus, school_name) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        val = (
            data.get('room'),
            data.get('floor'),
            data.get('building'),
            data.get('type'),
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


@app.route('/api/locations/<id>', methods=['PUT', 'DELETE'])
def manage_location_item(id):
    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response
    cursor = conn.cursor(dictionary=True)

    if request.method == 'DELETE':
        try:
            # Check for dependencies (Maintenance)
            cursor.execute(
                "SELECT COUNT(*) as count FROM Maintenance WHERE location_id = %s", (id,))
            if cursor.fetchone()['count'] > 0:
                return jsonify({"error": "Cannot delete location with associated maintenance tasks"}), 400

            cursor.execute(
                "DELETE FROM Location WHERE location_id = %s", (id,))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({"error": "Location not found"}), 404
            return jsonify({"message": "Location deleted"}), 200
        except mysql.connector.Error as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 400
        finally:
            cursor.close()
            conn.close()

    # PUT
    data, error_response = parse_json()
    if error_response:
        return error_response

    try:
        fields = []
        values = []
        for key in ['room', 'floor', 'building', 'type', 'campus', 'school_name']:
            if key in data:
                fields.append(f"{key} = %s")
                values.append(data[key])

        if not fields:
            return jsonify({"error": "No fields to update"}), 400

        values.append(id)
        sql = f"UPDATE Location SET {', '.join(fields)} WHERE location_id = %s"
        cursor.execute(sql, tuple(values))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Location not found"}), 404
        return jsonify({"message": "Location updated"}), 200
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
                SELECT
                    a.activity_id,
                    a.type,
                    a.time,
                    p.name AS organiser_name,
                    l.building,
                    l.room,
                    l.floor
                FROM Activity a
                JOIN Person p ON a.organiser_id = p.personal_id
                LEFT JOIN Location l ON a.location_id = l.location_id
                ORDER BY a.activity_id
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
        sql = "INSERT INTO Activity (activity_id, type, time, organiser_id, location_id) VALUES (%s, %s, %s, %s, %s)"
        val = (
            data['activity_id'],
            data.get('type'),
            data.get('time'),
            data['organiser_id'],
            data.get('location_id'),
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


@app.route('/api/activities/<id>', methods=['PUT', 'DELETE'])
def manage_activity_item(id):
    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response
    cursor = conn.cursor(dictionary=True)

    if request.method == 'DELETE':
        try:
            cursor.execute(
                "DELETE FROM Participation WHERE activity_id = %s", (id,))
            cursor.execute(
                "DELETE FROM Activity WHERE activity_id = %s", (id,))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({"error": "Activity not found"}), 404
            return jsonify({"message": "Activity deleted"}), 200
        except mysql.connector.Error as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 400
        finally:
            cursor.close()
            conn.close()

    # PUT
    data, error_response = parse_json()
    if error_response:
        return error_response

    try:
        fields = []
        values = []
        for key in ['type', 'time', 'organiser_id']:
            if key in data:
                fields.append(f"{key} = %s")
                values.append(data[key])

        if not fields:
            return jsonify({"error": "No fields to update"}), 400

        values.append(id)
        sql = f"UPDATE Activity SET {', '.join(fields)} WHERE activity_id = %s"
        cursor.execute(sql, tuple(values))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Activity not found"}), 404
        return jsonify({"message": "Activity updated"}), 200
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
        cursor.execute(
            "INSERT INTO Maintenance (type, frequency, location_id, active_chemical, contracted_company_id) VALUES (%s, %s, %s, %s, %s)",
            (data['type'], data.get('frequency'), data['location_id'], data.get(
                'active_chemical', False), data.get('contracted_company_id'))
        )
        conn.commit()
        return jsonify({"message": "Maintenance task created"}), 201
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


@app.route('/api/maintenance/<id>', methods=['PUT', 'DELETE'])
def manage_maintenance_item(id):
    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response
    cursor = conn.cursor(dictionary=True)

    if request.method == 'DELETE':
        try:
            cursor.execute(
                "DELETE FROM Maintenance WHERE maintenance_id = %s", (id,))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({"error": "Maintenance task not found"}), 404
            return jsonify({"message": "Maintenance task deleted"}), 200
        except mysql.connector.Error as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 400
        finally:
            cursor.close()
            conn.close()

    # PUT
    data, error_response = parse_json()
    if error_response:
        return error_response

    try:
        fields = []
        values = []
        for key in ['type', 'frequency', 'location_id', 'active_chemical', 'contracted_company_id']:
            if key in data:
                fields.append(f"{key} = %s")
                values.append(data[key])

        if not fields:
            return jsonify({"error": "No fields to update"}), 400

        values.append(id)
        sql = f"UPDATE Maintenance SET {', '.join(fields)} WHERE maintenance_id = %s"
        cursor.execute(sql, tuple(values))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Maintenance task not found"}), 404
        return jsonify({"message": "Maintenance task updated"}), 200
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
                       a.activity_id, a.type AS activity_type,
                       a.time AS activity_time,
                       l.building, l.room
                FROM Participation p
                JOIN Person per ON p.personal_id = per.personal_id
                JOIN Activity a ON p.activity_id = a.activity_id
                LEFT JOIN Location l ON a.location_id = l.location_id
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


# --- New Endpoints for Buildings, Supervision ---

# ExternalCompany Endpoints
@app.route('/api/external-companies', methods=['GET', 'POST'])
def manage_external_companies():
    if request.method == 'GET':
        conn, error_response = get_connection_or_response()
        if error_response:
            return error_response
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM ExternalCompany")
            return jsonify(cursor.fetchall()), 200
        finally:
            cursor.close()
            conn.close()

    data, error_response = parse_json(required_fields=['name'])
    if error_response:
        return error_response
    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("INSERT INTO ExternalCompany (name, contact_info) VALUES (%s, %s)",
                       (data['name'], data.get('contact_info')))
        conn.commit()
        return jsonify({"message": "External Company created"}), 201
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# --- Bulk Import Endpoint ---
@app.route('/api/import', methods=['POST'])
def bulk_import():
    data, error_response = parse_json(required_fields=['entity', 'items'])
    if error_response:
        return error_response

    entity = data['entity']
    items = data['items']

    if not isinstance(items, list):
        return jsonify({"error": "Items must be a list"}), 400

    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response
    cursor = conn.cursor(dictionary=True)

    try:
        if entity == 'persons':
            sql = "INSERT INTO Person (personal_id, name, age, gender, date_of_birth, supervisor_id) VALUES (%s, %s, %s, %s, %s, %s)"
            for item in items:
                val = (item.get('personal_id'), item.get('name'), item.get('age'), item.get(
                    'gender'), item.get('date_of_birth'), item.get('supervisor_id'))
                cursor.execute(sql, val)
        elif entity == 'locations':
            sql = "INSERT INTO Location (room, floor, building, type, campus, school_name) VALUES (%s, %s, %s, %s, %s, %s)"
            for item in items:
                val = (item.get('room'), item.get('floor'), item.get('building'), item.get(
                    'type'), item.get('campus'), item.get('school_name'))
                cursor.execute(sql, val)
        elif entity == 'activities':
            sql = "INSERT INTO Activity (activity_id, type, time, organiser_id) VALUES (%s, %s, %s, %s)"
            for item in items:
                val = (item.get('activity_id'), item.get('type'),
                       item.get('time'), item.get('organiser_id'))
                cursor.execute(sql, val)
        else:
            return jsonify({"error": "Unsupported entity for bulk import"}), 400

        conn.commit()
        return jsonify({"message": f"Successfully imported {len(items)} items"}), 201
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# --- Safety Search Endpoint ---
@app.route('/api/search/safety', methods=['GET'])
def safety_search():
    building = request.args.get('building')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response
    cursor = conn.cursor(dictionary=True)

    try:
        # Find cleaning activities or maintenance in the given building/time
        # Note: Maintenance table has frequency but not specific scheduled times in this schema
        # We will assume 'Maintenance' implies scheduled tasks, and we filter by building.
        # If Activity table had a 'Cleaning' type we could check that too, but Maintenance is the primary place for 'Cleaning'.

        query = """
            SELECT m.*, l.building, l.room, l.floor
            FROM Maintenance m
            JOIN Location l ON m.location_id = l.location_id
            WHERE m.type = 'Cleaning'
        """
        params = []

        if building:
            query += " AND l.building = %s"
            params.append(building)

        # Note: Since Maintenance doesn't have a specific 'date/time' field (only frequency),
        # we can't strictly filter by time range unless we assume some schedule.
        # However, the requirement is "Find scheduled cleaning activities...".
        # Given the schema limitations, we will return all cleaning tasks for the building
        # and let the frontend display them with their frequency.

        cursor.execute(query, tuple(params))
        results = cursor.fetchall()

        # Add warning flag
        for r in results:
            if r.get('active_chemical'):
                r['warning'] = "WARNING: Hazardous chemicals used!"

        return jsonify(results), 200
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
