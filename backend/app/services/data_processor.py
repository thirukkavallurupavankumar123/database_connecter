import pandas as pd
import numpy as np
from typing import Any


def compute_statistics(columns: list[str], data: list[dict]) -> dict[str, Any]:
    """Compute descriptive statistics on query results using Pandas/NumPy."""
    if not data:
        return {"row_count": 0, "columns": columns, "numeric_stats": {}, "categorical_stats": {}}

    df = pd.DataFrame(data)
    stats: dict[str, Any] = {
        "row_count": len(df),
        "columns": list(df.columns),
        "numeric_stats": {},
        "categorical_stats": {},
    }

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            series = df[col].dropna()
            if len(series) == 0:
                continue
            stats["numeric_stats"][col] = {
                "mean": round(float(np.mean(series)), 2),
                "median": round(float(np.median(series)), 2),
                "std": round(float(np.std(series)), 2),
                "min": round(float(np.min(series)), 2),
                "max": round(float(np.max(series)), 2),
                "sum": round(float(np.sum(series)), 2),
                "count": int(len(series)),
            }
        else:
            series = df[col].dropna()
            if len(series) == 0:
                continue
            value_counts = series.value_counts()
            stats["categorical_stats"][col] = {
                "unique_count": int(series.nunique()),
                "top_values": {str(k): int(v) for k, v in value_counts.head(10).items()},
                "count": int(len(series)),
            }

    return stats


def detect_trends(columns: list[str], data: list[dict]) -> list[str]:
    """Detect simple trends in the data for AI context."""
    if not data or len(data) < 2:
        return []

    df = pd.DataFrame(data)
    trends = []

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) < 2:
            continue

        # Simple trend: compare first half vs second half
        mid = len(series) // 2
        first_half_mean = series.iloc[:mid].mean()
        second_half_mean = series.iloc[mid:].mean()

        if first_half_mean > 0:
            change_pct = ((second_half_mean - first_half_mean) / first_half_mean) * 100
            if abs(change_pct) > 5:
                direction = "increased" if change_pct > 0 else "decreased"
                trends.append(
                    f"Column '{col}' {direction} by {abs(change_pct):.1f}% "
                    f"from first half to second half of results."
                )

    return trends
