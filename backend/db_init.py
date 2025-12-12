"""Database initialization / reset script for the CMMS project.

WARNING: Running this script will execute all SQL statements in
``backend/schema.sql``, including ``DROP TABLE IF EXISTS ...``. This means it
can **destroy existing tables and data** in the configured database.

Use this **only** for:
  - Initial setup on a new database, or
  - When you intentionally want to reset the schema and data for development.

Normal application runs should *not* use this script; they should just rely on
the existing database contents.
"""

from db import init_db

if __name__ == "__main__":
    print(
        "[db_init.py] WARNING: This will DROP and RECREATE tables defined in "
        "backend/schema.sql for the configured database."
    )
    print(
        "Use this only for initial setup or when you explicitly want to reset "
        "all data."
    )

    init_db()
