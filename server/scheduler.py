from __future__ import annotations

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from wx_engine.config import load_config
from wx_engine.manager import ForecastManager

logger = logging.getLogger(__name__)
config = load_config()
manager = ForecastManager(config)


def run_job():
    try:
        departure = datetime.now(tz=timezone.utc)
        manager.run(config.default_route, departure, config.vessel_speed)
        logger.info("Scheduled forecast complete")
    except Exception as exc:
        logger.exception("Scheduled forecast failed: %s", exc)


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_job, "cron", **cron_kwargs(config.scheduler_cron))
    scheduler.start()
    return scheduler


def cron_kwargs(expr: str):
    fields = expr.split()
    if len(fields) != 5:
        return {"minute": 0, "hour": "*/6"}
    minute, hour, day, month, dow = fields
    return {"minute": minute, "hour": hour, "day": day, "month": month, "day_of_week": dow}


__all__ = ["start_scheduler", "run_job"]
