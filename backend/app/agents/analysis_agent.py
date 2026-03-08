from groq import Groq
from app.config import get_settings

SYSTEM_PROMPT = """You are an expert data analyst AI assistant for enterprise analytics.

Given query results and statistics, you must:
1. Provide a clear, concise SUMMARY of the data (2-3 sentences).
2. Generate actionable INSIGHTS as a bullet list (3-5 insights).
3. Identify any notable TRENDS in the data.

Format your response EXACTLY as:
SUMMARY:
<your summary here>

INSIGHTS:
- <insight 1>
- <insight 2>
- <insight 3>

TRENDS:
- <trend 1>
- <trend 2>

Be specific with numbers. Reference actual values from the data.
Use business-friendly language suitable for executives and analysts.
"""


def analyze_data(natural_language_query: str, columns: list[str],
                 data: list[dict], statistics: dict,
                 trends: list[str]) -> dict:
    """Use Groq LLM to generate insights and summary from query results."""
    settings = get_settings()
    client = Groq(api_key=settings.GROQ_API_KEY)

    # Build a data sample for the prompt (first 20 rows to keep token count manageable)
    sample_rows = data[:20]
    data_preview = _format_data_preview(columns, sample_rows)

    user_prompt = f"""Original question: {natural_language_query}

Result columns: {', '.join(columns)}
Total rows returned: {len(data)}

Data preview (first {len(sample_rows)} rows):
{data_preview}

Statistics:
{_format_statistics(statistics)}

Detected trends:
{chr(10).join(trends) if trends else 'No clear trends detected.'}

Analyze this data and provide your summary, insights, and trends:"""

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=1024,
    )

    raw_text = response.choices[0].message.content.strip()
    return _parse_analysis_response(raw_text)


def _format_data_preview(columns: list[str], rows: list[dict]) -> str:
    """Format data rows into a readable text table for the AI prompt."""
    if not rows:
        return "No data."
    lines = [" | ".join(columns)]
    lines.append("-" * len(lines[0]))
    for row in rows:
        lines.append(" | ".join(str(row.get(c, "")) for c in columns))
    return "\n".join(lines)


def _format_statistics(stats: dict) -> str:
    """Format statistics dict into readable text."""
    parts = []
    for col, s in stats.get("numeric_stats", {}).items():
        parts.append(
            f"  {col}: mean={s['mean']}, median={s['median']}, "
            f"std={s['std']}, min={s['min']}, max={s['max']}, sum={s['sum']}"
        )
    for col, s in stats.get("categorical_stats", {}).items():
        top = ", ".join(f"{k}({v})" for k, v in list(s["top_values"].items())[:5])
        parts.append(f"  {col}: {s['unique_count']} unique values. Top: {top}")
    return "\n".join(parts) if parts else "No statistics available."


def _parse_analysis_response(text: str) -> dict:
    """Parse the structured AI response into a dict."""
    result = {"summary": "", "insights": [], "trends": []}

    current_section = None
    for line in text.split("\n"):
        stripped = line.strip()
        upper = stripped.upper()

        if upper.startswith("SUMMARY:"):
            current_section = "summary"
            remainder = stripped[len("SUMMARY:"):].strip()
            if remainder:
                result["summary"] = remainder
            continue
        elif upper.startswith("INSIGHTS:"):
            current_section = "insights"
            continue
        elif upper.startswith("TRENDS:"):
            current_section = "trends"
            continue

        if current_section == "summary" and stripped:
            result["summary"] += (" " + stripped) if result["summary"] else stripped
        elif current_section == "insights" and stripped.startswith("- "):
            result["insights"].append(stripped[2:])
        elif current_section == "trends" and stripped.startswith("- "):
            result["trends"].append(stripped[2:])

    return result
