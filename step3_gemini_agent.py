import os
import psycopg2
from dotenv import load_dotenv
import google.generativeai as genai

# -----------------------------------------------------------------------------
# 1. ENVIRONMENT & API KEY CONFIGURATION
# -----------------------------------------------------------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("\n[ERROR] GEMINI_API_KEY not found in .env file.")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# -----------------------------------------------------------------------------
# 2. DATABASE CONFIGURATION
# -----------------------------------------------------------------------------
DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": "5432"
}

# -----------------------------------------------------------------------------
# 3. RBAC GATEKEEPER TOOL
# -----------------------------------------------------------------------------
CURRENT_LOGGED_IN_USER_ID = 101  # Alice

def get_user_expenses(requested_emp_id: int) -> str:
    """Looks up the expense history for an employee by their employee ID."""
    print(f"\n[BACKEND LOG] Executing DB Tool for Emp_ID: {requested_emp_id}")

    # RBAC Security Gate
    if requested_emp_id != CURRENT_LOGGED_IN_USER_ID:
        return f"ACCESS DENIED. You can only view data for user {CURRENT_LOGGED_IN_USER_ID}."

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT description, amount, status FROM expenses WHERE emp_id = %s",
            (requested_emp_id,)
        )
        results = cursor.fetchall()

        if not results:
            return "No expenses found."

        output = "Expense Records:\n"
        for row in results:
            output += f"- Item: {row[0]}, Amount: ${row[1]}, Status: {row[2]}\n"
        return output

    except Exception as e:
        return f"Database error: {e}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# -----------------------------------------------------------------------------
# 4. GEMINI AGENT RUNNER (NATIVE SDK)
# -----------------------------------------------------------------------------
def run_gemini_agent():
    print("\n=== ENTERPRISE EXPENSE BOT (GEMINI NATIVE SDK) ===")

    # Debug: List available models
    print("\nAvailable models supporting generateContent:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f" - {m.name}")
    print("-" * 50)

    # Configure tool
    model = genai.GenerativeModel(
        model_name="gemini-3.1-pro-preview",
        tools=[get_user_expenses],
        system_instruction=(
            "You are an expense assistant. Current user is Alice (ID: 101). "
            "Use get_user_expenses for any request about financial data."
        )
    )

    chat = model.start_chat(enable_automatic_function_calling=True)

    while True:
        try:
            user_input = input("Alice: ")
            if user_input.lower() in ('exit', 'quit'):
                break

            response = chat.send_message(user_input)
            print(f"\nAgent: {response.text}\n")
        except Exception as e:
            print(f"\n[ERROR]: {e}\n")

if __name__ == "__main__":
    run_gemini_agent()
