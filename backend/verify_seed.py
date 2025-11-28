import mysql.connector
from db import get_db_connection


def verify_seed():
    conn = get_db_connection()
    if conn is None:
        return
    cursor = conn.cursor(dictionary=True)

    print("Verifying Seed Data...")

    # 1. Check Cleaning with Chemicals
    cursor.execute(
        "SELECT COUNT(*) as count FROM Maintenance WHERE type='Cleaning' AND chemical_used=1")
    chem_count = cursor.fetchone()['count']
    print(f"Cleaning tasks with chemicals: {chem_count}")

    # 2. Check Contracted Maintenance
    cursor.execute(
        "SELECT COUNT(*) as count FROM Maintenance WHERE contracted_company_id IS NOT NULL")
    contract_count = cursor.fetchone()['count']
    print(f"Contracted maintenance tasks: {contract_count}")

    # 3. Check Building Supervision
    cursor.execute("SELECT COUNT(*) as count FROM BuildingSupervision")
    supervision_count = cursor.fetchone()['count']
    print(f"Building supervisions: {supervision_count}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    verify_seed()
