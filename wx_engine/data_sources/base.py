"""Base downloader utilities."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict

import requests

logger = logging.getLogger(__name__)


class DownloaderError(Exception):
    pass


class BaseDownloader:
    model: str = "base"

    def __init__(self, base_dir: str, bbox, hours):
        self.base_dir = Path(base_dir)
        self.bbox = bbox
        self.hours = hours
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def fetch(self, cycle: str) -> Dict[int, Path]:
        raise NotImplementedError

    def download_file(self, url: str, dest: Path) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            logger.info("%s already exists, skipping", dest)
            return dest
        logger.info("Downloading %s", url)
        resp = requests.get(url, timeout=120)
        if resp.status_code != 200:
            raise DownloaderError(f"Failed to download {url}: {resp.status_code}")
        dest.write_bytes(resp.content)
        return dest


__all__ = ["BaseDownloader", "DownloaderError"]
