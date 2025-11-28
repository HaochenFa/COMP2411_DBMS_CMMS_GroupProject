import mysql.connector
from db import get_db_connection
import random
from datetime import datetime, timedelta


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
        tables = [
            "Maintenance",
            "Participation", "Affiliation", "Activity", "Location",
            "ExternalCompany", "School", "Profile", "Person"
        ]
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE {table}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # --- 1. Schools ---
        schools = [
            ('School of Computing', 'COMP', 'Faculty of Engineering'),
            ('School of Design', 'SD', 'Faculty of Design'),
            ('Faculty of Business', 'FB', 'Faculty of Business'),
            ('Department of Engineering', 'ENG', 'Faculty of Engineering'),
            ('School of Hotel & Tourism', 'SHTM', 'Faculty of Business')
        ]
        cursor.executemany(
            "INSERT INTO School (school_name, department, faculty, hq_location_id) VALUES (%s, %s, %s, NULL)", schools)
        print(f"Inserted {cursor.rowcount} schools.")

        # --- 2. External Companies ---
        companies = [
            ('CleanCo Ltd.', 'contact@cleanco.com'),
            ('SecureGuard Inc.', 'security@secureguard.com'),
            ('FixItAll Services', 'support@fixitall.com'),
            ('GreenThumb Landscaping', 'info@greenthumb.com'),
            ('TechSolutions', 'help@techsolutions.com')
        ]
        cursor.executemany(
            "INSERT INTO ExternalCompany (name, contact_info) VALUES (%s, %s)", companies)
        print(f"Inserted {cursor.rowcount} external companies.")

        # Get Company IDs
        cursor.execute("SELECT company_id FROM ExternalCompany")
        company_ids = [row[0] for row in cursor.fetchall()]

        # --- 3. Buildings (as simple list for location seeding) ---
        buildings = [
            ('PQ Wing', 'Core Campus'),
            ('Z Block', 'North Campus'),
            ('V Block', 'South Campus'),
            ('Y Block', 'East Campus'),
            ('A Block', 'Core Campus'),
            ('M Block', 'West Campus'),
            ('Li Ka Shing Tower', 'Core Campus'),
            ('Jockey Club Innovation Tower', 'North Campus'),
            ('Student Halls', 'Residential Area'),
            ('Library', 'Core Campus')
        ]
        # Buildings are now just string attributes in Location, no separate table

        # --- 4. People ---
        first_names = ["Alice", "Bob", "Charlie", "Diana", "Evan", "Fiona", "George",
                       "Hannah", "Ian", "Julia", "Kevin", "Liam", "Mia", "Noah", "Olivia"]
        last_names = ["Smith", "Jones", "Brown", "Prince", "Wright", "Lee",
                      "Wong", "Chan", "Ho", "Taylor", "Wilson", "Evans", "Thomas", "Roberts"]

        people_data = []
        supervisor_ids = []

        # Create 10 Supervisors first
        for i in range(1, 11):
            pid = f"S{i:03d}"
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            age = random.randint(35, 60)
            gender = random.choice(['Male', 'Female'])
            dob = (datetime.now() - timedelta(days=age*365)).strftime('%Y-%m-%d')
            people_data.append((pid, name, age, gender, dob, None))
            supervisor_ids.append(pid)

        # Create 40 Regular Staff/Students
        for i in range(1, 41):
            pid = f"P{i:03d}"
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            age = random.randint(18, 50)
            gender = random.choice(['Male', 'Female'])
            dob = (datetime.now() - timedelta(days=age*365)).strftime('%Y-%m-%d')
            supervisor = random.choice(
                supervisor_ids) if random.random() > 0.3 else None
            people_data.append((pid, name, age, gender, dob, supervisor))

        cursor.executemany(
            "INSERT INTO Person (personal_id, name, age, gender, date_of_birth, supervisor_id) VALUES (%s, %s, %s, %s, %s, %s)", people_data)
        print(f"Inserted {cursor.rowcount} people.")

        # --- 5. Profiles ---
        profiles_data = []
        roles = ['Academic', 'Maintenance', 'Student',
                 'Administrator', 'Mid-level Manager', 'Base-level Worker']
        for p in people_data:
            pid = p[0]
            role = random.choice(roles)
            status = 'Current' if random.random() > 0.1 else 'Former'
            profiles_data.append((pid, role, status))

        cursor.executemany(
            "INSERT INTO Profile (personal_id, job_role, status) VALUES (%s, %s, %s)", profiles_data)
        print(f"Inserted {cursor.rowcount} profiles.")

        # --- 6. Affiliations ---
        affiliations_data = []
        school_names = [s[0] for s in schools]
        for p in people_data:
            pid = p[0]
            # Assign 1 or 2 affiliations
            for _ in range(random.randint(1, 2)):
                school = random.choice(school_names)
                if (pid, school) not in affiliations_data:
                    affiliations_data.append((pid, school))

        cursor.executemany(
            "INSERT INTO Affiliation (personal_id, school_name) VALUES (%s, %s)", affiliations_data)
        print(f"Inserted {cursor.rowcount} affiliations.")

        # --- 7. Locations ---
        building_names = [b[0] for b in buildings]
        locations_data = []
        loc_types = ['Room', 'Lecture Hall',
                     'Lab', 'Office', 'Corridor', 'Garden']

        for i in range(1, 41):  # 40 Locations
            b_name = random.choice(building_names)
            # Find campus for this building
            campus = next(b[1] for b in buildings if b[0] == b_name)

            room_no = f"{random.randint(1, 9)}{random.randint(0, 9):02d}"
            floor = room_no[0]
            l_type = random.choice(loc_types)
            school = random.choice(school_names)

            locations_data.append(
                (room_no, floor, b_name, l_type, campus, school))

        cursor.executemany(
            "INSERT INTO Location (room, floor, building, type, campus, school_name) VALUES (%s, %s, %s, %s, %s, %s)", locations_data)
        print(f"Inserted {cursor.rowcount} locations.")

        # Get Location IDs
        cursor.execute("SELECT location_id FROM Location")
        location_ids = [row[0] for row in cursor.fetchall()]

        # --- 8.1 Update Schools with HQ Locations ---
        # Assign a random location to each school as HQ
        for school in schools:
            hq_loc_id = random.choice(location_ids)
            cursor.execute(
                "UPDATE School SET hq_location_id = %s WHERE school_name = %s", (hq_loc_id, school[0]))
        print(f"Updated {len(schools)} schools with HQ locations.")

        # --- 9. Activities ---
        activities_data = []
        act_types = ['Lecture', 'Seminar', 'Workshop',
                     'Meeting', 'Exam', 'Social Event']

        for i in range(1, 31):  # 30 Activities
            aid = f"A{i:03d}"
            a_type = random.choice(act_types)
            # Random time in next 30 days
            time = datetime.now() + timedelta(days=random.randint(1, 30),
                                              hours=random.randint(8, 18))
            organiser = random.choice(people_data)[0]
            location_id = random.choice(location_ids)
            activities_data.append((aid, a_type, time, organiser, location_id))

        cursor.executemany(
            "INSERT INTO Activity (activity_id, type, time, organiser_id, location_id) VALUES (%s, %s, %s, %s, %s)", activities_data)
        print(f"Inserted {cursor.rowcount} activities.")

        # --- 10. Participations ---
        participation_data = []
        activity_ids = [a[0] for a in activities_data]

        for aid in activity_ids:
            # 3-8 participants per activity
            num_participants = random.randint(3, 8)
            participants = random.sample(
                [p[0] for p in people_data], num_participants)
            for pid in participants:
                participation_data.append((pid, aid))

        cursor.executemany(
            "INSERT INTO Participation (personal_id, activity_id) VALUES (%s, %s)", participation_data)
        print(f"Inserted {cursor.rowcount} participations.")

        # --- 11. Maintenance ---
        maintenance_data = []
        m_types = ['Repair', 'Cleaning',
                   'Security', 'Inspection', 'Renovation']
        frequencies = ['Daily', 'Weekly', 'Monthly', 'Yearly', 'One-off']

        for i in range(50):  # 50 Tasks
            m_type = random.choice(m_types)
            freq = random.choice(frequencies)
            lid = random.choice(location_ids)

            # Logic for Chemical Used (Safety Search)
            chemical_used = False
            if m_type == 'Cleaning' and random.random() > 0.5:
                chemical_used = True

            # Logic for Contracted Company
            company_id = None
            if random.random() > 0.6:  # 40% chance of being contracted
                company_id = random.choice(company_ids)

            maintenance_data.append(
                (m_type, freq, lid, chemical_used, company_id))

        cursor.executemany(
            "INSERT INTO Maintenance (type, frequency, location_id, active_chemical, contracted_company_id) VALUES (%s, %s, %s, %s, %s)", maintenance_data)
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
