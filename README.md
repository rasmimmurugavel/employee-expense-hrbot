# Employee Expense & HR Assistant Bot

This project is an enterprise-grade AI architecture demonstration that replaces legacy "form-based" HR tooling with a secure, intent-driven conversational interface. The focus is on **deterministic orchestration**—making an LLM act as a safe, compliant agent within an organization.

## The Problem
Enterprises require secure financial and HR workflows. Naive AI implementations fail here because of three key risks:
- **RBAC Violation**: Chatbots often lack identity awareness and can access unauthorized financial data.
- **Liability/Hallucination**: AI is trained on generic web data, leading it to invent policies that create legal and financial liability (e.g., approving $8,000 corporate flights).
- **Control**: Large Language Models are probabilistic and cannot be trusted to unilaterally write to financial databases.

## The Architectural Solution

| Feature | Enterprise Problem | AI Solution Implemented |
| :--- | :--- | :--- |
| **RBAC** | Unauthorized access to employee salary/expense data. | **Identity-Bound Tools**: Tools derive user identity from the authenticated session, not user input. |
| **RAG** | Hallucinated policy advice, creating legal liability. | **Policy-Grounded Retrieval**: Constraint-based prompt engineering forces adherence to local policy docs. |
| **Safety** | LLM unilaterally approving/submitting false expenses. | **Human-in-the-Loop**: Transactional tools force "Pending Approval" states for high-value claims. |

---

## Architecture Breakdown

### 1. Robust RBAC (Role-Based Access Control)
Instead of asking an LLM to "check authorization," which is prone to prompt injection, we decouple identity from the AI. The Python backend simulates a secure Single Sign-On (SSO) session. When an employee asks a financial question, the tool tool executes `SELECT` statements using only the `employee_id` hardcoded into the Python session scope. The LLM never touches, sees, or handles identity.

### 2. The RAG Boundary (Retrieval-Augmented Generation)
RAG ensures the AI retrieves internal, verified facts rather than relying on its pre-trained "knowledge." 
- **The Tool**: `search_policy_docs` reads local markdown files (the "Source of Truth").
- **The Boundary**: System instructions explicitly forbid the AI from speculating: "If the info is not in the text, you must reply: 'Please ask HR.' Do not guess."

### 3. Orchestration Logic (The Agent)
The "Backend Loop" works as a sequence of three steps:
1. **Parsing**: The LLM analyzes the user prompt and selects a registered Python tool.
2. **Deterministic Execution**: Python performs the execution (PostgreSQL query) to get real-world data.
3. **Synthesis**: The LLM receives the real data and summarizes it for the user.

---

## Step-by-Step Implementation

1. **Database Setup**: Initialized PostgreSQL with normalized tables (`employees`, `expenses`) to reflect institutional data schemas.
2. **Tool Creation**: Developed Python functions decorated as tools, ensuring that each function acts as an "API" that the AI can call, but which enforces internal organizational rules.
3. **Local Inference**: Deployed local LLM models using **Ollama** to bypass public API quota limits, reduce latency, and ensure data privacy (no sensitive HR data leaves the machine).
4. **Agentic Loop**: Built a Python chat loop that orchestrates communication between the Ollama server and the本地 Postgres database instance.

---

## How to Set Up Your Database
To create a password for your user in PostgreSQL so your Python script can connect:

1. Open your terminal and run: `psql -d postgres`
2. Run this command: `ALTER USER your_username_here WITH PASSWORD 'your_password_here';`
3. Update `DB_PARAMS` in `step3_ollama_agent.py` to match:
```python
DB_PARAMS = {
    "dbname": "postgres",
    "user": "your_username_here",
    "password": "your_password_here",
    "host": "localhost",
    "port": "5432"
}
```

---

## Future Improvements
- **Vector Database**: For large-scale policy docs, replace simple keyword search with `pgvector` or `ChromaDB` for semantic retrieval.
- **Formal Workflow Engine**: Replace the simple `insert_expense` tool with an integration into a formal workflow engine (like Temporal or Camunda) for enterprise-grade approval state machines.
