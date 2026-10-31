import sqlite3

# Connect database
def connect_database(db: str):
    conn = sqlite3.connect(db)
    # To use it like a dict
    conn.row_factory = sqlite3.Row
    return conn

