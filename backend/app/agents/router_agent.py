from __future__ import annotations

import json
from typing import Any

from groq import Groq

from app.config import get_settings


SYSTEM_PROMPT = """You are an expert enterprise data routing assistant.

Your ONLY job is to choose the single best database CONNECTION for answering
an analytics question, given a list of available connections.

RULES:
1. You MUST return a single JSON object with exactly these keys:
   {"connection_id": "<id>", "reason": "<short explanation>"}
2. The value of "connection_id" MUST be one of the provided connection ids.
3. Prefer the default connection when the question is generic or ambiguous.
4. Use labels and tags to understand business domains (e.g., sales, support,
   marketing, HR, finance, product analytics, etc.).
5. Prefer connections whose labels/tags clearly match the question topic.
6. If multiple connections could work, choose the one that seems most
   enterprise-relevant and broadly useful.
7. NEVER invent a new connection id.
8. Do not include any explanation outside the JSON itself.
"""


def _parse_json_object(text: str) -> dict[str, Any]:
    """Extract the first JSON object from the model response.

    The router is instructed to return pure JSON, but this is defensive in
    case any extra text is added.
    """

    text = text.strip()

    # Fast path: try to parse as-is
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    # Fallback: find first {...} block
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass

    raise ValueError("Could not parse JSON object from router agent response")


def select_connection_with_agent(
    natural_language_query: str,
    connections: list[dict[str, Any]],
    organization_name: str | None = None,
    default_connection_id: str | None = None,
) -> dict[str, Any]:
    """Use Groq LLM to choose the best connection for a query.

    Returns a dict with keys: "connection_id" and "reason".
    """

    if not connections:
        raise ValueError("No connections provided to routing agent")

    settings = get_settings()
    client = Groq(api_key=settings.GROQ_API_KEY)

    org_part = f"Organization: {organization_name}\n" if organization_name else ""

    connections_json = json.dumps(connections, indent=2)

    user_prompt = f"""{org_part}User question: {natural_language_query}

Available connections (JSON array):
{connections_json}

Default connection id (may be null): {json.dumps(default_connection_id)}

Choose the single best connection for this question and return ONLY a JSON object
with keys connection_id and reason.
"""

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=256,
    )

    raw_text = response.choices[0].message.content.strip()
    obj = _parse_json_object(raw_text)

    if "connection_id" not in obj or not isinstance(obj["connection_id"], str):
        raise ValueError("Router agent response missing valid 'connection_id'")

    return obj
