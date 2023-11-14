from datetime import datetime

import sqlite3


def connect_to_database():
    """
    Connects to the database and creates a table if it does not exist.

    Returns:
        conn (Connection): The connection object to the database.
        cursor (Cursor): The cursor object to execute SQL statements.
    """
    conn = sqlite3.connect("log.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            prompt TEXT,
            completion TEXT
        )
    """
    )
    conn.commit()
    return conn, cursor


def log_error(prompt, error_message):
    """
    Logs an error message to the database.

    Parameters:
    - prompt (str): The prompt received in the request.
    - error_message (str): The error message to be logged.

    Returns:
    - None
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Connect to the database
    conn, cursor = connect_to_database()

    # Insert the error message into the logs table
    cursor.execute(
        "INSERT INTO logs (timestamp, prompt, completion) VALUES (?, ?, ?)",
        (timestamp, prompt, error_message),
    )

    # Commit changes and close the database connection
    conn.commit()
    close_database_connection(conn)


def close_database_connection(conn):
    """
    Closes the database connection.

    Args:
        conn: The database connection to be closed.

    Returns:
        None
    """
    conn.close()