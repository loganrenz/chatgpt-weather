"""GFS 0.25 degree downloader."""
from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Dict

from wx_engine.data_sources.base import BaseDownloader


GFS_BASE = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod"


class GFSDownloader(BaseDownloader):
    model = "gfs"

    def fetch(self, cycle: str | None = None) -> Dict[int, Path]:
        """Download GFS GRIB2 files for configured hours.

        cycle format: YYYYMMDDHH. Defaults to latest 00/06/12/18 before now.
        """
        if not cycle:
            now = dt.datetime.utcnow()
            hour = (now.hour // 6) * 6
            if hour == 24:
                hour = 18
            cycle = (now.replace(hour=hour, minute=0, second=0, microsecond=0)).strftime("%Y%m%d%H")
        day = cycle[:8]
        hour = cycle[8:]
        folder = f"gfs.{day}/{hour}/atmos"
        paths: Dict[int, Path] = {}
        for fhour in self.hours:
            fn = f"gfs.t{hour}z.pgrb2.0p25.f{fhour:03d}"
            url = f"{GFS_BASE}/{folder}/{fn}"
            dest = self.base_dir / "gfs" / day / hour / fn
            try:
                paths[fhour] = self.download_file(url, dest)
            except Exception:
                continue
        return paths


__all__ = ["GFSDownloader"]
