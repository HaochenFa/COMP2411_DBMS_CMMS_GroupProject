import mysql.connector
from db import get_db_connection


def seed_data():
    conn = get_db_connection()
    if conn is None:
        print("Failed to connect to database.")
        return

    cursor = conn.cursor()

    try:
        print("Seeding data...")

        # Clear existing data
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE Participation")
        cursor.execute("TRUNCATE TABLE Affiliation")
        cursor.execute("TRUNCATE TABLE Maintenance")
        cursor.execute("TRUNCATE TABLE Activity")
        cursor.execute("TRUNCATE TABLE Location")
        cursor.execute("TRUNCATE TABLE Profile")
        cursor.execute("TRUNCATE TABLE Person")
        cursor.execute("TRUNCATE TABLE School")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # 1. Schools
        schools = [
            ('School of Computing', 'COMP', 'Faculty of Engineering'),
            ('School of Design', 'SD', 'Faculty of Design'),
            ('Faculty of Business', 'FB', 'Faculty of Business'),
            ('Department of Engineering', 'ENG', 'Faculty of Engineering')
        ]
        cursor.executemany(
            "INSERT INTO School (school_name, department, faculty) VALUES (%s, %s, %s)", schools)
        print(f"Inserted {cursor.rowcount} schools.")

        # 2. People
        people = [
            ('P001', 'Alice Smith', 30, 'Female', '1993-05-15', None),
            ('P002', 'Bob Jones', 45, 'Male', '1978-11-20', None),
            ('P003', 'Charlie Brown', 22, 'Male', '2001-02-10', 'P001'),
            ('P004', 'Diana Prince', 28, 'Female', '1995-08-25', 'P002'),
            ('P005', 'Evan Wright', 35, 'Male', '1988-12-05', None)
        ]
        cursor.executemany(
            "INSERT INTO Person (personal_id, name, age, gender, date_of_birth, supervisor_id) VALUES (%s, %s, %s, %s, %s, %s)", people)
        print(f"Inserted {cursor.rowcount} people.")

        # 3. Profiles
        profiles = [
            ('P001', 'Professor', 'Current'),
            ('P002', 'Administrator', 'Current'),
            ('P003', 'Student', 'Current'),
            ('P004', 'Researcher', 'Former'),
            ('P005', 'Technician', 'Current')
        ]
        cursor.executemany(
            "INSERT INTO Profile (personal_id, job_role, status) VALUES (%s, %s, %s)", profiles)
        print(f"Inserted {cursor.rowcount} profiles.")

        # 4. Affiliations
        affiliations = [
            ('P001', 'School of Computing'),
            ('P002', 'Faculty of Business'),
            ('P003', 'School of Design'),
            ('P004', 'School of Computing'),
            ('P005', 'Department of Engineering')
        ]
        cursor.executemany(
            "INSERT INTO Affiliation (personal_id, school_name) VALUES (%s, %s)", affiliations)
        print(f"Inserted {cursor.rowcount} affiliations.")

        # 5. Locations
        locations = [
            ('101', '1', 'PQ Wing', 'Core Campus', 'School of Design'),
            ('205', '2', 'Z Block', 'North Campus', 'School of Computing'),
            ('301', '3', 'V Block', 'South Campus', 'Faculty of Business'),
            ('G01', 'G', 'Y Block', 'East Campus', 'Department of Engineering')
        ]
        cursor.executemany(
            "INSERT INTO Location (room, floor, building, campus, school_name) VALUES (%s, %s, %s, %s, %s)", locations)
        print(f"Inserted {cursor.rowcount} locations.")

        # Get Location IDs
        cursor.execute("SELECT location_id, building FROM Location")
        location_map = {building: id for id, building in cursor.fetchall()}

        # 6. Activities
        activities = [
            ('A001', 'Lecture', '2024-11-01 10:00:00', 'P001'),
            ('A002', 'Event', '2024-12-05 14:00:00', 'P002'),
            ('A003', 'Seminar', '2024-10-20 09:00:00', 'P001'),
            ('A004', 'Workshop', '2024-11-15 11:00:00', 'P005')
        ]
        cursor.executemany(
            "INSERT INTO Activity (activity_id, type, time, organiser_id) VALUES (%s, %s, %s, %s)", activities)
        print(f"Inserted {cursor.rowcount} activities.")

        # 7. Participations
        participations = [
            ('P003', 'A001'),
            ('P001', 'A002'),
            ('P004', 'A001'),
            ('P003', 'A002'),
            ('P002', 'A003')
        ]
        cursor.executemany(
            "INSERT INTO Participation (personal_id, activity_id) VALUES (%s, %s)", participations)
        print(f"Inserted {cursor.rowcount} participations.")

        # 8. Maintenance
        maintenance_tasks = [
            ('Repair', 'Monthly', location_map['Z Block']),
            ('Renovation', 'Yearly', location_map['PQ Wing']),
            ('Cleaning', 'Weekly', location_map['V Block']),
            ('Security', 'Daily', location_map['Y Block']),
            ('Repair', 'Monthly', location_map['Z Block'])
        ]
        cursor.executemany(
            "INSERT INTO Maintenance (type, frequency, location_id) VALUES (%s, %s, %s)", maintenance_tasks)
        print(f"Inserted {cursor.rowcount} maintenance tasks.")

        conn.commit()
        print("Data seeding completed successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    seed_data()
