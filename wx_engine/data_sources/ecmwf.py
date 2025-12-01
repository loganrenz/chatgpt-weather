"""ECMWF open data downloader stub."""
from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Dict

from wx_engine.data_sources.base import BaseDownloader


ECMWF_BASE = "https://data.ecmwf.int/forecasts"


class ECMWFDownloader(BaseDownloader):
    model = "ecmwf"

    def fetch(self, cycle: str | None = None) -> Dict[int, Path]:
        """Download ECMWF open data GRIB files.

        This uses the public open-data layout. The bbox cropping is left to the decoder.
        """
        if not cycle:
            now = dt.datetime.utcnow()
            hour = 0 if now.hour < 12 else 12
            cycle = now.replace(hour=hour, minute=0, second=0, microsecond=0).strftime("%Y%m%d%H")
        day = cycle[:8]
        hour = cycle[8:]
        paths: Dict[int, Path] = {}
        for fhour in self.hours:
            # ECMWF open data uses steps like 0,3,... with file naming pattern
            step = f"{fhour:03d}"
            fn = f"{day}/{hour}/0p4-beta/oper_fc_sfc_{cycle}_{step}.grib2"
            url = f"{ECMWF_BASE}/{fn}"
            dest = self.base_dir / "ecmwf" / day / hour / f"oper_fc_sfc_{cycle}_{step}.grib2"
            try:
                paths[fhour] = self.download_file(url, dest)
            except Exception:
                continue
        return paths


__all__ = ["ECMWFDownloader"]
