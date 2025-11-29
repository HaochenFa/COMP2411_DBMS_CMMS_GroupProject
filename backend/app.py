from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from db import get_db_connection, init_db, is_db_initialized
import mysql.connector
from datetime import datetime

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
            # Check for role filter parameter
            role_filter = request.args.get('role')

            if role_filter:
                # Filter persons by job_role from Profile table
                cursor.execute("""
                    SELECT p.personal_id, p.name, p.gender, p.date_of_birth, p.entry_date, p.supervisor_id,
                           TIMESTAMPDIFF(YEAR, p.date_of_birth, CURDATE()) AS age,
                           pr.job_role
                    FROM Person p
                    JOIN Profile pr ON p.personal_id = pr.personal_id
                    WHERE pr.job_role = %s
                """, (role_filter,))
            else:
                # Calculate age dynamically from date_of_birth
                cursor.execute("""
                    SELECT personal_id, name, gender, date_of_birth, entry_date, supervisor_id,
                           TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) AS age
                    FROM Person
                """)
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
            "INSERT INTO Person (personal_id, name, gender, date_of_birth, supervisor_id) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        val = (
            data['personal_id'],
            data['name'],
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
        # Dynamic update query (age is calculated, not stored)
        fields = []
        values = []
        if 'name' in data:
            fields.append("name = %s")
            values.append(data['name'])
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


# --- School/Department Endpoints ---
@app.route('/api/schools', methods=['GET', 'POST'])
def manage_schools():
    if request.method == 'GET':
        conn, error_response = get_connection_or_response()
        if error_response:
            return error_response

        cursor = conn.cursor(dictionary=True)
        try:
            # Return with school_name alias for frontend compatibility
            cursor.execute("""
                SELECT department, dept_name AS school_name, faculty, hq_building
                FROM School
                WHERE faculty IS NOT NULL
            """)
            schools = cursor.fetchall()
            return jsonify(schools), 200
        except mysql.connector.Error as e:
            return jsonify({"error": str(e)}), 400
        finally:
            cursor.close()
            conn.close()

    # POST - department is now the PK, school_name is the dept_name
    data, error_response = parse_json(
        required_fields=['department', 'school_name'])
    if error_response:
        return error_response

    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        sql = "INSERT INTO School (department, dept_name, faculty, hq_building) VALUES (%s, %s, %s, %s)"
        val = (data['department'], data['school_name'],
               data.get('faculty'), data.get('hq_building'))
        cursor.execute(sql, val)
        conn.commit()
        return jsonify({"message": "Department created"}), 201
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


@app.route('/api/schools/<id>', methods=['PUT', 'DELETE'])
def manage_school_item(id):
    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response
    cursor = conn.cursor(dictionary=True)

    if request.method == 'DELETE':
        try:
            # Delete related affiliations first
            cursor.execute(
                "DELETE FROM Affiliation WHERE department = %s", (id,))
            # Set department to NULL for related locations
            cursor.execute(
                "UPDATE Location SET department = NULL WHERE department = %s", (id,))
            # Delete the department
            cursor.execute("DELETE FROM School WHERE department = %s", (id,))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({"error": "Department not found"}), 404
            return jsonify({"message": "Department deleted"}), 200
        except mysql.connector.Error as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 400
        finally:
            cursor.close()
            conn.close()

    # PUT - school_name in data maps to dept_name in DB
    data, error_response = parse_json()
    if error_response:
        return error_response

    try:
        fields = []
        values = []
        field_mapping = {'school_name': 'dept_name',
                         'faculty': 'faculty', 'hq_building': 'hq_building'}
        for key, db_field in field_mapping.items():
            if key in data:
                fields.append(f"{db_field} = %s")
                values.append(data[key])

        if not fields:
            return jsonify({"error": "No fields to update"}), 400

        values.append(id)
        sql = f"UPDATE School SET {', '.join(fields)} WHERE department = %s"
        cursor.execute(sql, tuple(values))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Department not found"}), 404
        return jsonify({"message": "Department updated"}), 200
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
                SELECT l.*, s.dept_name, s.faculty
                FROM Location l
                LEFT JOIN School s ON l.department = s.department
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
            "INSERT INTO Location (room, floor, building, type, campus, department) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        val = (
            data.get('room'),
            data.get('floor'),
            data.get('building'),
            data.get('type'),
            data.get('campus'),
            data.get('department'),
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
        for key in ['room', 'floor', 'building', 'type', 'campus', 'department']:
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


# Affiliation (Person-Department)
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
                       a.department, s.dept_name AS school_name
                FROM Affiliation a
                JOIN Person p ON a.personal_id = p.personal_id
                JOIN School s ON a.department = s.department
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
        required_fields=['personal_id', 'department'])
    if error_response:
        return error_response

    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        sql = "INSERT INTO Affiliation (personal_id, department) VALUES (%s, %s)"
        val = (data['personal_id'], data['department'])
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


# Report 4: Department Statistics
@app.route('/api/reports/school-stats', methods=['GET'])
def school_stats():
    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        query = (
            """
            SELECT s.department, s.dept_name AS school_name, s.faculty,
                   COUNT(DISTINCT a.personal_id) AS affiliated_people,
                   COUNT(DISTINCT l.location_id) AS locations_count
            FROM School s
            LEFT JOIN Affiliation a ON s.department = a.department
            LEFT JOIN Location l ON s.department = l.department
            GROUP BY s.department, s.dept_name, s.faculty
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
            sql = "INSERT INTO Person (personal_id, name, gender, date_of_birth, supervisor_id) VALUES (%s, %s, %s, %s, %s)"
            for item in items:
                val = (item.get('personal_id'), item.get('name'), item.get(
                    'gender'), item.get('date_of_birth'), item.get('supervisor_id'))
                cursor.execute(sql, val)
        elif entity == 'locations':
            sql = "INSERT INTO Location (room, floor, building, type, campus, department) VALUES (%s, %s, %s, %s, %s, %s)"
            for item in items:
                val = (item.get('room'), item.get('floor'), item.get('building'), item.get(
                    'type'), item.get('campus'), item.get('department'))
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
    """Find scheduled cleaning activities with optional time period filtering.

    Query parameters:
    - building: Filter by building name
    - start_time: Filter by scheduled_time >= start_time (format: YYYY-MM-DD or YYYY-MM-DDTHH:MM)
    - end_time: Filter by scheduled_time <= end_time (format: YYYY-MM-DD or YYYY-MM-DDTHH:MM)
    """
    building = request.args.get('building')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT m.maintenance_id, m.type, m.frequency, m.active_chemical,
                   m.scheduled_time, m.end_time,
                   l.building, l.room, l.floor, l.campus,
                   ec.name as company_name
            FROM Maintenance m
            JOIN Location l ON m.location_id = l.location_id
            LEFT JOIN ExternalCompany ec ON m.contracted_company_id = ec.company_id
            WHERE m.type = 'Cleaning'
        """
        params = []

        if building:
            query += " AND l.building = %s"
            params.append(building)

        # Filter by time period using scheduled_time column
        if start_time:
            query += " AND m.scheduled_time >= %s"
            params.append(start_time)

        if end_time:
            query += " AND m.scheduled_time <= %s"
            params.append(end_time)

        query += " ORDER BY m.scheduled_time ASC"

        cursor.execute(query, tuple(params))
        results = cursor.fetchall()

        # Add warning flag for hazardous chemicals
        for r in results:
            if r.get('active_chemical'):
                r['warning'] = "⚠️ WARNING: Hazardous chemicals used!"
            # Format dates for frontend display
            if r.get('scheduled_time'):
                r['scheduled_time'] = r['scheduled_time'].isoformat() if hasattr(
                    r['scheduled_time'], 'isoformat') else str(r['scheduled_time'])
            if r.get('end_time'):
                r['end_time'] = r['end_time'].isoformat() if hasattr(
                    r['end_time'], 'isoformat') else str(r['end_time'])

        return jsonify(results), 200
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# --- Manager Building Report Endpoint ---
@app.route('/api/reports/manager-buildings', methods=['GET'])
def get_manager_building_report():
    """Get report showing managers with their supervised buildings and related maintenance activities."""
    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        # Get all supervision assignments with manager details and maintenance counts
        cursor.execute("""
            SELECT
                bs.personal_id,
                p.name as manager_name,
                bs.building,
                bs.assigned_date,
                COUNT(DISTINCT m.maintenance_id) as maintenance_count,
                SUM(CASE WHEN m.active_chemical = 1 THEN 1 ELSE 0 END) as chemical_maintenance_count
            FROM BuildingSupervision bs
            JOIN Person p ON bs.personal_id = p.personal_id
            LEFT JOIN Location l ON l.building = bs.building
            LEFT JOIN Maintenance m ON m.location_id = l.location_id
            GROUP BY bs.supervision_id, bs.personal_id, p.name, bs.building, bs.assigned_date
            ORDER BY p.name, bs.building
        """)
        supervisions = cursor.fetchall()

        # Group by manager for a hierarchical report
        managers = {}
        for s in supervisions:
            mgr_id = s['personal_id']
            if mgr_id not in managers:
                managers[mgr_id] = {
                    'personal_id': mgr_id,
                    'name': s['manager_name'],
                    'buildings': []
                }
            managers[mgr_id]['buildings'].append({
                'building': s['building'],
                'assigned_date': s['assigned_date'].isoformat() if hasattr(s['assigned_date'], 'isoformat') else str(s['assigned_date']) if s['assigned_date'] else None,
                'maintenance_count': s['maintenance_count'],
                'chemical_maintenance_count': s['chemical_maintenance_count']
            })

        return jsonify({
            'data': list(managers.values()),
            'summary': {
                'total_managers': len(managers),
                'total_supervisions': len(supervisions)
            }
        }), 200
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# --- PDF Report Generation Endpoints ---

@app.route('/api/reports/comprehensive-data', methods=['GET'])
def get_comprehensive_report_data():
    """Get all data needed for comprehensive PDF report generation."""
    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        report_data = {}

        # Summary counts
        cursor.execute("SELECT COUNT(*) as count FROM Person")
        total_persons = cursor.fetchone()['count']

        cursor.execute(
            "SELECT COUNT(*) as count FROM School WHERE faculty IS NOT NULL")
        total_schools = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM Activity")
        total_activities = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM Maintenance")
        total_maintenance = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM Location")
        total_locations = cursor.fetchone()['count']

        report_data['summary'] = {
            'total_persons': total_persons,
            'total_schools': total_schools,
            'total_activities': total_activities,
            'total_maintenance': total_maintenance,
            'total_locations': total_locations,
            'generated_at': datetime.now().isoformat()
        }

        # Maintenance summary
        cursor.execute("""
            SELECT m.type, l.building, l.campus, COUNT(*) AS count
            FROM Maintenance m
            JOIN Location l ON m.location_id = l.location_id
            GROUP BY m.type, l.building, l.campus
            ORDER BY count DESC
        """)
        report_data['maintenance_summary'] = cursor.fetchall()

        # People summary
        cursor.execute("""
            SELECT pr.job_role, pr.status, COUNT(*) AS count
            FROM Profile pr
            GROUP BY pr.job_role, pr.status
            ORDER BY pr.job_role, count DESC
        """)
        report_data['people_summary'] = cursor.fetchall()

        # Activities summary
        cursor.execute("""
            SELECT a.type, p.name AS organiser_name, COUNT(*) AS activity_count
            FROM Activity a
            JOIN Person p ON a.organiser_id = p.personal_id
            GROUP BY a.type, p.name
            ORDER BY activity_count DESC
        """)
        report_data['activities_summary'] = cursor.fetchall()

        # School stats
        cursor.execute("""
            SELECT s.department, s.dept_name AS school_name, s.faculty,
                   COUNT(DISTINCT a.personal_id) AS affiliated_people,
                   COUNT(DISTINCT l.location_id) AS locations_count
            FROM School s
            LEFT JOIN Affiliation a ON s.department = a.department
            LEFT JOIN Location l ON s.department = l.department
            GROUP BY s.department, s.dept_name, s.faculty
        """)
        report_data['school_stats'] = cursor.fetchall()

        # Maintenance frequency
        cursor.execute("""
            SELECT frequency, type, COUNT(*) AS task_count
            FROM Maintenance
            GROUP BY frequency, type
            ORDER BY frequency, task_count DESC
        """)
        report_data['maintenance_frequency'] = cursor.fetchall()

        # Safety data (cleaning tasks with chemicals)
        cursor.execute("""
            SELECT m.*, l.building, l.room, l.floor
            FROM Maintenance m
            JOIN Location l ON m.location_id = l.location_id
            WHERE m.type = 'Cleaning'
        """)
        report_data['safety_data'] = cursor.fetchall()

        return jsonify(report_data), 200

    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


@app.route('/api/reports/generate-pdf', methods=['POST'])
def generate_pdf_report():
    """Generate and return a PDF report."""
    # Import here to avoid circular imports and allow graceful failure
    try:
        from pdf_service import generate_report
    except ImportError as e:
        return jsonify({
            "error": "PDF generation not available. Please install required packages: "
                     "pip install reportlab matplotlib pandas Pillow"
        }), 500

    # Parse request options
    data = request.get_json(silent=True) or {}
    sections = data.get('sections', [
        'executive_summary', 'maintenance', 'personnel',
        'activities', 'schools', 'safety'
    ])

    # Fetch comprehensive data
    conn, error_response = get_connection_or_response()
    if error_response:
        return error_response

    cursor = conn.cursor(dictionary=True)
    try:
        report_data = {}

        # Summary counts
        cursor.execute("SELECT COUNT(*) as count FROM Person")
        total_persons = cursor.fetchone()['count']

        cursor.execute(
            "SELECT COUNT(*) as count FROM School WHERE faculty IS NOT NULL")
        total_schools = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM Activity")
        total_activities = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM Maintenance")
        total_maintenance = cursor.fetchone()['count']

        report_data['summary'] = {
            'total_persons': total_persons,
            'total_schools': total_schools,
            'total_activities': total_activities,
            'total_maintenance': total_maintenance,
        }

        # Maintenance summary
        cursor.execute("""
            SELECT m.type, l.building, l.campus, COUNT(*) AS count
            FROM Maintenance m
            JOIN Location l ON m.location_id = l.location_id
            GROUP BY m.type, l.building, l.campus
            ORDER BY count DESC
        """)
        report_data['maintenance_summary'] = cursor.fetchall()

        # People summary
        cursor.execute("""
            SELECT pr.job_role, pr.status, COUNT(*) AS count
            FROM Profile pr
            GROUP BY pr.job_role, pr.status
        """)
        report_data['people_summary'] = cursor.fetchall()

        # Activities summary
        cursor.execute("""
            SELECT a.type, p.name AS organiser_name, COUNT(*) AS activity_count
            FROM Activity a
            JOIN Person p ON a.organiser_id = p.personal_id
            GROUP BY a.type, p.name
            ORDER BY activity_count DESC
        """)
        report_data['activities_summary'] = cursor.fetchall()

        # School stats
        cursor.execute("""
            SELECT s.department, s.dept_name AS school_name, s.faculty,
                   COUNT(DISTINCT a.personal_id) AS affiliated_people,
                   COUNT(DISTINCT l.location_id) AS locations_count
            FROM School s
            LEFT JOIN Affiliation a ON s.department = a.department
            LEFT JOIN Location l ON s.department = l.department
            GROUP BY s.department, s.dept_name, s.faculty
        """)
        report_data['school_stats'] = cursor.fetchall()

        # Maintenance frequency
        cursor.execute("""
            SELECT frequency, type, COUNT(*) AS task_count
            FROM Maintenance
            GROUP BY frequency, type
        """)
        report_data['maintenance_frequency'] = cursor.fetchall()

        # Safety data
        cursor.execute("""
            SELECT m.*, l.building, l.room, l.floor
            FROM Maintenance m
            JOIN Location l ON m.location_id = l.location_id
            WHERE m.type = 'Cleaning'
        """)
        report_data['safety_data'] = cursor.fetchall()

        # Generate PDF
        pdf_buffer = generate_report(report_data, sections)

        # Return PDF response
        filename = f"CMMS_Report_{datetime.now().strftime('%Y-%m-%d')}.pdf"
        return Response(
            pdf_buffer.getvalue(),
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'application/pdf'
            }
        )

    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


# =====================
# Building Supervision Endpoints
# =====================


@app.route('/api/building-supervision', methods=['GET'])
def get_building_supervisions():
    """Get all building supervision assignments."""
    conn, err = get_connection_or_response()
    if err:
        return err
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT bs.supervision_id, bs.personal_id, bs.building, bs.assigned_date,
                   p.name as manager_name
            FROM BuildingSupervision bs
            JOIN Person p ON bs.personal_id = p.personal_id
            ORDER BY bs.building, p.name
        """)
        supervisions = cursor.fetchall()
        return jsonify({"data": supervisions})
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/building-supervision', methods=['POST'])
def create_building_supervision():
    """Assign a manager to supervise a building."""
    data, err = parse_json(required_fields=['personal_id', 'building'])
    if err:
        return err

    conn, err = get_connection_or_response()
    if err:
        return err

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO BuildingSupervision (personal_id, building, assigned_date)
            VALUES (%s, %s, CURRENT_DATE)
        """, (data['personal_id'], data['building']))
        conn.commit()
        return jsonify({"message": "Supervision assignment created", "id": cursor.lastrowid}), 201
    except mysql.connector.IntegrityError as e:
        if "Duplicate entry" in str(e):
            return jsonify({"error": "This manager is already assigned to this building"}), 400
        return jsonify({"error": str(e)}), 400
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/building-supervision/<int:supervision_id>', methods=['DELETE'])
def delete_building_supervision(supervision_id):
    """Remove a building supervision assignment."""
    conn, err = get_connection_or_response()
    if err:
        return err

    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM BuildingSupervision WHERE supervision_id = %s", (supervision_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Supervision assignment not found"}), 404
        conn.commit()
        return jsonify({"message": "Supervision assignment deleted"})
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/building-supervision/by-manager/<personal_id>', methods=['GET'])
def get_supervisions_by_manager(personal_id):
    """Get all buildings supervised by a specific manager."""
    conn, err = get_connection_or_response()
    if err:
        return err
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT bs.supervision_id, bs.building, bs.assigned_date
            FROM BuildingSupervision bs
            WHERE bs.personal_id = %s
            ORDER BY bs.building
        """, (personal_id,))
        supervisions = cursor.fetchall()
        return jsonify({"data": supervisions})
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/building-supervision/by-building/<building>', methods=['GET'])
def get_supervisions_by_building(building):
    """Get all managers supervising a specific building."""
    conn, err = get_connection_or_response()
    if err:
        return err
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT bs.supervision_id, bs.personal_id, bs.assigned_date,
                   p.name as manager_name
            FROM BuildingSupervision bs
            JOIN Person p ON bs.personal_id = p.personal_id
            WHERE bs.building = %s
            ORDER BY p.name
        """, (building,))
        supervisions = cursor.fetchall()
        return jsonify({"data": supervisions})
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    # Optionally initialize the DB on first run. This will only call the
    # destructive init_db() if the core tables are missing.
    ensure_db_initialized_on_startup()
    app.run(debug=True, host='0.0.0.0', port=5050)
