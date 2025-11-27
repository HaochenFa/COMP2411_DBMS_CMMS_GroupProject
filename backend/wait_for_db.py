import os
import time

import mysql.connector
from mysql.connector import Error


def wait_for_db(max_attempts: int = 30, delay_seconds: int = 2) -> None:
    """Block until the MySQL server is reachable or the timeout is reached.

    This checks only that we can open a connection to the server (not that the
    target database already exists). The actual schema creation is handled by
    ``init_db()``/``ensure_db_initialized_on_startup()`` in app.py.
    """

    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")

    for attempt in range(1, max_attempts + 1):
        try:
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
            )
            if conn.is_connected():
                print(
                    f"[wait_for_db] Connected to MySQL at {host} on attempt {attempt}."
                )
                conn.close()
                return
        except Error as exc:
            print(
                f"[wait_for_db] MySQL not ready yet (attempt {attempt}/{max_attempts}): {exc}"
            )
        time.sleep(delay_seconds)

    print(
        f"[wait_for_db] Gave up waiting for MySQL after "
        f"{max_attempts * delay_seconds} seconds. "
        "The application may still start but could fail if the DB is not ready."
    )


if __name__ == "__main__":
    wait_for_db()
