from groq import Groq
from app.config import get_settings

SYSTEM_PROMPT = """You are an expert SQL query generator for enterprise databases.

Your ONLY job is to convert natural language questions into valid, read-only SQL queries.

RULES:
1. Generate ONLY SELECT or WITH (CTE) queries. NEVER use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or any DDL/DML.
2. Always use the exact table and column names from the provided schema.
3. Return ONLY the SQL query — no explanations, no markdown, no code fences.
4. Use appropriate aggregations (SUM, COUNT, AVG, etc.) when the question implies them.
5. Use GROUP BY when aggregating, and ORDER BY for ranked/sorted results.
6. Use LIMIT when the user asks for "top N" results.
7. Use proper date/time functions based on the database dialect.
8. If the question is ambiguous, make reasonable assumptions and generate the most useful query.
9. Always alias complex expressions for readability.
10. Never use SELECT * — specify the needed columns explicitly.
"""


def generate_sql(natural_language_query: str, schema_context: str,
                 db_type: str = "postgresql") -> str:
    """Use Groq LLM to convert a natural language query into SQL."""
    settings = get_settings()
    client = Groq(api_key=settings.GROQ_API_KEY)

    user_prompt = f"""Database type: {db_type}

{schema_context}

User question: {natural_language_query}

Generate the SQL query:"""

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=1024,
    )

    sql = response.choices[0].message.content.strip()

    # Clean up common LLM formatting artifacts
    if sql.startswith("```"):
        lines = sql.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        sql = "\n".join(lines).strip()

    return sql
