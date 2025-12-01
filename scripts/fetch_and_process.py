#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime

from wx_engine.config import load_config
from wx_engine.manager import ForecastManager


def main():
    parser = argparse.ArgumentParser(description="Fetch GRIB data and generate forecast")
    parser.add_argument("--route", default=None, help="Route ID")
    parser.add_argument("--departure", required=False, help="Departure ISO time (UTC)")
    parser.add_argument("--speed", type=float, default=None, help="Speed over ground in knots")
    args = parser.parse_args()

    cfg = load_config()
    route = args.route or cfg.default_route
    departure = datetime.fromisoformat(args.departure) if args.departure else datetime.utcnow()
    speed = args.speed or cfg.vessel_speed

    manager = ForecastManager(cfg)
    manager.run(route, departure, speed)
    print("Forecast generated for", route)


if __name__ == "__main__":
    main()
