"""Timeline utilities."""
from __future__ import annotations

from datetime import timezone
from typing import List

import pandas as pd


def annotate_timeline(series: List[dict]) -> List[dict]:
    """Add local time info and friendly labels to timeline points."""
    annotated: List[dict] = []
    for row in series:
        t = row.get("time_utc")
        if t is None:
            continue
        local = t.astimezone(timezone.utc).astimezone(pd.Timestamp.now().tz)
        annotated.append({
            **row,
            "time_iso": t.isoformat(),
            "time_local": local.isoformat(),
        })
    return annotated


__all__ = ["annotate_timeline"]
