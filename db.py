import os
import psycopg
from psycopg import OperationalError
import pandas as pd


def get_db_connection():
    # Connection parameters
    host = os.getenv("DB_HOST", "127.0.0.1")
    dbname = os.getenv("DB_NAME", "postgres")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv(
        "DB_PASSWORD", "password"
    )  # Default password, override with environment variable
    port = os.getenv("DB_PORT", "5432")

    # Establishing the connection
    try:
        conn = psycopg.connect(
            dbname=dbname, user=user, password=password, host=host, port=port
        )
        return conn
    except OperationalError as e:
        print(f"The error '{e}' occurred")
        return None


if __name__ == "__main__":
    conn = get_db_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute("SELECT * FROM people")
        rows = cur.fetchall()
        df = pd.DataFrame(rows)
        print(df)
        print("Connection established")
        print("Connection established")
    else:
        print("Connection not established")
