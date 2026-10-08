import os
import psycopg2
import ollama
from dotenv import load_dotenv

# 1. DATABASE CONFIGURATION
DB_PARAMS = {
    "dbname": "postgres", "user": "postgres", "password": "password", "host": "localhost", "port": "5432"
}
CURRENT_LOGGED_IN_USER_ID = 101

# 2. RAG & RBAC TOOLS
def get_my_expenses() -> str:
    """Retrieves the expense history for the currently logged-in user (Alice)."""
    return get_user_expenses(101)

def get_user_expenses(requested_emp_id: int) -> str:
    """Internal tool to look up expense history by employee ID."""
    print(f"[DEBUG] Inside get_user_expenses, requested_emp_id: {requested_emp_id}")
    if requested_emp_id != CURRENT_LOGGED_IN_USER_ID:
        return "ACCESS DENIED."
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute("SELECT description, amount, status FROM expenses WHERE emp_id = %s", (requested_emp_id,))
        results = cursor.fetchall()
        print(f"[DEBUG] DB Results: {results}")
        return "\n".join([f"- {r[0]}: ${r[1]} ({r[2]})" for r in results]) if results else "No expenses."
    except Exception as e:
        print(f"[DEBUG] DB Error: {e}")
        return f"Database error: {e}"
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def search_policy_docs(query: str) -> str:
    """Searches company policy documents for expense and HR rules."""
    policy_file = "company_policy.md"
    if not os.path.exists(policy_file): return "Policy not found."
    with open(policy_file, "r") as f: content = f.read()
    results = [line for line in content.split('\n') if query.lower() in line.lower()]
    return "\n".join(results) if results else "NO_POLICY_FOUND"

# 3. AGENTIC LOOP
def run_ollama_agent():
    print("\n=== ENTERPRISE EXPENSE BOT (OLLAMA FINAL) ===")

    tools = [get_my_expenses, search_policy_docs]
    messages = [
        {"role": "system", "content": (
            "You are an expense assistant. "
            "1. IF queried about Alice's expenses, ALWAYS call `get_my_expenses()`. "
            "2. IF queried about policy, ALWAYS call `search_policy_docs`. "
            "3. If info is missing, say: 'I cannot provide advice on this, please ask HR.' "
            "NEVER guess, NEVER explain yourself unless requested."
        )}
    ]

    while True:
        user_input = input("\nAlice: ")
        if user_input.lower() in ('exit', 'quit'): break
        messages.append({"role": "user", "content": user_input})

        # Call Ollama
        response = ollama.chat(model='llama3.1', messages=messages, tools=tools)
        messages.append(response['message'])

        if response['message'].get('tool_calls'):
            for tool_call in response['message']['tool_calls']:
                func_name = tool_call['function']['name']
                print(f"[DEBUG] Tool call: {func_name}")

                result = ""
                if func_name == 'get_my_expenses':
                    result = get_my_expenses()
                elif func_name == 'search_policy_docs':
                    query = tool_call['function']['arguments'].get('query', 'expense')
                    result = search_policy_docs(query=query)

                print(f"[DEBUG] Tool '{func_name}' returned: {result}")
                messages.append({"role": "tool", "content": str(result), "name": func_name})

            final_response = ollama.chat(model='llama3.1', messages=messages)
            print(f"\nAgent: {final_response['message']['content']}")
            messages.append(final_response['message'])
        else:
            print(f"\nAgent: {response['message']['content']}")

if __name__ == "__main__":
    run_ollama_agent()
