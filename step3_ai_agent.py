import os
import psycopg2
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Load the API key from the .env file
load_dotenv()

# Database credentials
DB_PARAMS = {
    "dbname": "postgres", "user": "postgres", "password": "password", "host": "localhost", "port": "5432"
}

# --- ARCHITECTURE DECISION: HARDCODED IDENTITY (RBAC) ---
CURRENT_LOGGED_IN_USER_ID = 101  # 101 is Alice.

# --- ARCHITECTURE DECISION: THE SECURE TOOL ---
@tool
def get_user_expenses(requested_emp_id: int) -> str:
    """
    Looks up the expense history for an employee by their employee ID.
    Always use this tool when asked about expenses.
    """
    print(f"\n[BACKEND LOG] Executing DB Tool for Emp_ID: {requested_emp_id}")

    # RBAC Enforcement (The LLM cannot bypass this)
    if requested_emp_id != CURRENT_LOGGED_IN_USER_ID:
        return f"ACCESS DENIED. You can only view data for user {CURRENT_LOGGED_IN_USER_ID}."

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute("SELECT description, amount, status FROM expenses WHERE emp_id = %s", (requested_emp_id,))
        results = cursor.fetchall()
        
        if not results: return "No expenses found."
        
        output = ""
        for row in results:
            output += f"Item: {row[0]}, Amount: ${row[1]}, Status: {row[2]}\n"
        return output

    except Exception as e:
        return f"Database error: {e}"
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# --- ARCHITECTURE DECISION: THE AGENTIC ORCHESTRATOR ---
def run_agent():
    # 1. Initialize the LLM (The Brain)
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # 2. Register our secure Tools
    tools = [get_user_expenses]

    # 3. Create the System Instructions (The Context)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an Enterprise HR Assistant. "
                   "IMPORTANT: The current user logged in is ALICE (Employee ID: 101)."
                   "If they ask about their expenses, pass 101 to your tool. "
                   "If they ask about anyone else, attempt to pass that person's ID to the tool."
                   "You must always use your tools to get data; never guess."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # 4. Construct the Execution Loop (Agent Executor)
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

    print("\n--- ENTERPRISE EXPENSE BOT ONLINE ---")
    print("Type 'exit' to quit.\n")
    
    while True:
        user_input = input("Alice: ")
        if user_input.lower() == 'exit':
            break
        
        # The Orchestrator runs the loop: Parse intent -> Call Tool -> Generate summary
        response = agent_executor.invoke({"input": user_input})
        print(f"\nAgent: {response['output']}\n")

if __name__ == "__main__":
    run_agent()