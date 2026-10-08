import psycopg2
from typing import Optional
from langchain_core.tools import tool

# Your database credentials
DB_PARAMS = {
    "dbname": "postgres", "user": "postgres", "password": "password", "host": "localhost", "port": "5432"
}

# ---------------------------------------------------------
# SIMULATING THE LOGGED-IN SYSTEM USER
# In Oracle, this is passed securely from the SSO login session.
# We will simulate that Alice (ID: 101) is logged into our app.
# ---------------------------------------------------------
CURRENT_LOGGED_IN_USER_ID = 101  # 101 is Alice. 202 is Bob.

# ---------------------------------------------------------
# THE TOOL
# The @tool decorator tells LangChain: "This is an action the AI can take."
# ---------------------------------------------------------
@tool
def get_user_expenses(requested_emp_id: int) -> str:
    """
    Looks up the expense history for an employee. 
    Pass the employee ID to this tool to get their data.
    """
    print(f"\n[SYSTEM ALERT]: The AI is attempting to run the database tool for Employee ID: {requested_emp_id}...")

    # === THIS IS THE CRUCIAL ENTERPRISE RBAC CHECK ===
    # If the ID requested by the AI doesn't match the person logged in, WE BLOCK IT.
    if requested_emp_id != CURRENT_LOGGED_IN_USER_ID:
        # We don't crash. We return an error text back to the AI.
        return f"ACCESS DENIED. Security Error: You cannot access data for user {requested_emp_id}. You only have permission to view your own data."

    # If security passes, we connect to the DB and get the data
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()

        # Notice we hardcode requested_emp_id in the WHERE clause safely
        cursor.execute("SELECT description, amount, status FROM expenses WHERE emp_id = %s", (requested_emp_id,))
        results = cursor.fetchall()
        
        if not results:
            return "No expenses found."

        # Format the SQL rows into readable text so the AI can understand it later
        formatted_output = "Expense History:\n"
        for row in results:
            formatted_output += f"- {row[0]}: ${row[1]} ({row[2]})\n"

        return formatted_output

    except Exception as e:
        return f"Database error: {e}"
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# ---------------------------------------------------------
# TESTING THE TOOL (Without AI)
# Let's pretend the AI decided to call this function.
# ---------------------------------------------------------
if __name__ == "__main__":
    print(f"--- Simulating App Startup ---")
    print(f"Logged in user ID: {CURRENT_LOGGED_IN_USER_ID} (Alice)")

    # Test 1: Alice asks the AI for her own data (Valid)
    print("\nTest 1: AI tries to fetch Alice's data (ID: 101)")
    result1 = get_user_expenses.invoke({"requested_emp_id": 101})
    print(f"Database returned to AI:\n{result1}")

    # Test 2: Alice acts malicious and asks the AI for Bob's data (Unauthorized)
    print("\nTest 2: AI tries to fetch Bob's data (ID: 202)")
    result2 = get_user_expenses.invoke({"requested_emp_id": 202})
    print(f"Database returned to AI:\n{result2}")