import psycopg2

# Try connecting without a password
DB_PARAMS = {
    "dbname": "postgres",
    "user": "rasmi",
    "password": "",
    "host": "localhost",
    "port": "5432"
}

def test_connection():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        print("Successfully connected to Postgres!")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_connection()
