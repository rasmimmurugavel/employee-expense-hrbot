import psycopg2

# Update these with your PostgreSQL credentials
DB_PARAMS = {
    "dbname": "postgres",  # The name of your database
    "user": "postgres",    # Your postgres username
    "password": "", # Your postgres password
    "host": "localhost",
    "port": "5432"
}

def setup_database():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_PARAMS)
        conn.autocommit = True  # Allows us to create tables smoothly
        cursor = conn.cursor()

        print("Connected to PostgreSQL successfully...")

        # Create the Employees table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                emp_id INTEGER PRIMARY KEY,
                name VARCHAR(100),
                role VARCHAR(100),
                department VARCHAR(100)
            )
        ''')

        # Create the Expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                expense_id SERIAL PRIMARY KEY,
                emp_id INTEGER,
                amount DECIMAL(10,2),
                description TEXT,
                status VARCHAR(50)
            )
        ''')

        # Clear old data if you run this multiple times
        cursor.execute("TRUNCATE TABLE expenses, employees RESTART IDENTITY;")

        # Alice is a Junior Developer, Bob is her Manager
        cursor.execute('''
            INSERT INTO employees (emp_id, name, role, department) VALUES 
            (101, 'Alice', 'Junior Developer', 'Engineering'),
            (202, 'Bob', 'Senior Manager', 'Engineering');
        ''')

        # Insert some past expenses
        cursor.execute('''
            INSERT INTO expenses (emp_id, amount, description, status) VALUES 
            (101, 45.50, 'Team Lunch', 'APPROVED'),
            (202, 1200.00, 'Client Dinner', 'APPROVED'),
            (202, 3500.00, 'Executive Retreat', 'APPROVED');
        ''')

        print("Step 1 Complete: Tables created and populated with Alice and Bob!")

    except Exception as e:
        print(f"Database error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    setup_database()