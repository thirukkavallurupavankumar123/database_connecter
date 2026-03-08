import re


# Dangerous SQL keywords that must NEVER appear in generated queries
BLOCKED_KEYWORDS = [
    "DELETE", "DROP", "TRUNCATE", "ALTER", "CREATE", "INSERT",
    "UPDATE", "GRANT", "REVOKE", "EXEC", "EXECUTE", "MERGE",
    "CALL", "SET", "COMMIT", "ROLLBACK", "SAVEPOINT",
]

# Pattern to detect multiple statements (semicolons followed by more SQL)
MULTI_STATEMENT_PATTERN = re.compile(r";\s*\S", re.IGNORECASE)

# Comments that could hide malicious SQL
COMMENT_PATTERN = re.compile(r"(--|/\*|\*/)", re.IGNORECASE)


class SQLValidationError(Exception):
    """Raised when a generated SQL query fails safety validation."""
    pass


def validate_sql(sql: str) -> str:
    """Validate that a SQL query is safe to execute (read-only).
    Returns the cleaned SQL or raises SQLValidationError."""

    if not sql or not sql.strip():
        raise SQLValidationError("Empty SQL query")

    cleaned = sql.strip().rstrip(";").strip()

    # Must start with SELECT or WITH (CTEs)
    upper = cleaned.upper().lstrip()
    if not (upper.startswith("SELECT") or upper.startswith("WITH")):
        raise SQLValidationError(
            "Only SELECT and WITH (CTE) queries are allowed. "
            f"Query starts with: {cleaned.split()[0]}"
        )

    # Check for blocked keywords
    # Tokenize to avoid false positives in string literals or column names
    sql_upper = cleaned.upper()
    for keyword in BLOCKED_KEYWORDS:
        # Match keyword as a standalone word (not part of a column/table name)
        pattern = rf"\b{keyword}\b"
        if re.search(pattern, sql_upper):
            raise SQLValidationError(
                f"Blocked keyword detected: {keyword}. "
                "Only read-only queries are permitted."
            )

    # No multiple statements
    if MULTI_STATEMENT_PATTERN.search(cleaned):
        raise SQLValidationError(
            "Multiple SQL statements detected. Only single queries are allowed."
        )

    # No SQL comments (could hide malicious code)
    if COMMENT_PATTERN.search(cleaned):
        raise SQLValidationError(
            "SQL comments are not allowed in generated queries."
        )

    return cleaned
