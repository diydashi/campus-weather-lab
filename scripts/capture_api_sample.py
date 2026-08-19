"""保存少量、可读且不含敏感信息的真实 API 响应样例。"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from campus_weather.client import OpenMeteoClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    client = OpenMeteoClient(timeout=15.0)
    locations = client.search_city("南京", count=1)
    if not locations:
        raise RuntimeError("地理编码接口没有返回南京")

    location = locations[0]
    forecast = client.forecast(location.latitude, location.longitude, forecast_days=1)
    hourly = forecast["hourly"]
    sample = {
        "captured_at_local": datetime.now().astimezone().isoformat(timespec="seconds"),
        "purpose": "实验一真实 REST 接口响应样例，仅保留前 3 个小时",
        "location": {
            "name": location.name,
            "country_code": location.country_code,
            "latitude": location.latitude,
            "longitude": location.longitude,
        },
        "forecast_metadata": {
            "timezone": forecast["timezone"],
            "utc_offset_seconds": forecast["utc_offset_seconds"],
            "hourly_units": forecast["hourly_units"],
        },
        "first_three_hours": {
            key: values[:3]
            for key, values in hourly.items()
            if key in {"time", "temperature_2m", "precipitation_probability", "wind_speed_10m"}
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(sample, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
