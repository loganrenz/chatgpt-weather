"""Markdown/HTML briefing generation."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List

import markdown
import pandas as pd

from wx_engine.analysis.hazards import detect_hazards, risk_assessment
from wx_engine.interp.interpolator import summarize_series


def build_markdown(route_name: str, model: str, series: List[dict]) -> str:
    summary = summarize_series(series)
    hazards = detect_hazards(series)
    risk = risk_assessment(series)
    lines = [f"# Marine Weather Brief – {route_name} ({model.upper()})"]
    lines.append(f"Issued: {datetime.now(tz=timezone.utc).isoformat()}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Peak wind: {summary.get('max_wind', 0):.1f} kt")
    lines.append(f"- Peak gust: {summary.get('max_gust', 0):.1f} kt")
    lines.append(f"- Max significant wave height: {summary.get('max_swh', 0):.1f} m")
    lines.append(f"- Risk: **{risk}**")
    lines.append("")
    lines.append("## Hazards")
    if hazards:
        for h in hazards:
            lines.append(f"- {h}")
    else:
        lines.append("- None detected from available fields")
    lines.append("")
    lines.append("## Timeline (UTC)")
    df = pd.DataFrame(series)
    if not df.empty:
        df = df[[c for c in ["time_utc", "wind_dir", "wind_speed", "gust", "swh", "dwp", "mwd", "mslp", "prate"] if c in df]]
        lines.append(df.to_markdown(index=False))
    else:
        lines.append("No data available for timeline")
    return "\n".join(lines)


def markdown_to_html(md_text: str) -> str:
    return markdown.markdown(md_text, extensions=["tables", "fenced_code"])


__all__ = ["build_markdown", "markdown_to_html"]
