"""可重复的 CPU 与内存性能跟踪工作负载。"""

from __future__ import annotations

import argparse
import json
import time
import tracemalloc
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from campus_weather.risk import assess_hour


PROJECT_ROOT = Path(__file__).parents[1]
DEFAULT_DATA = PROJECT_ROOT / "data" / "sample_weather.json"
RISK_WEIGHTS = {"适宜出行": 1, "高温": 2, "低温": 3, "建议带伞": 5, "注意大风": 7}


@dataclass(frozen=True)
class WeatherRecord:
    time: str
    temperature: float
    rain_probability: float
    wind_speed: float


def load_records(path: Path = DEFAULT_DATA) -> list[WeatherRecord]:
    """从固定 JSON 数据中加载并对齐小时记录。"""

    payload = json.loads(path.read_text(encoding="utf-8"))
    hourly = payload["hourly"]
    fields = [
        hourly["time"],
        hourly["temperature_2m"],
        hourly["precipitation_probability"],
        hourly["wind_speed_10m"],
    ]
    if len({len(values) for values in fields}) != 1:
        raise ValueError("sample data arrays must have equal length")
    return [WeatherRecord(str(t), float(temp), float(rain), float(wind)) for t, temp, rain, wind in zip(*fields)]


def _risk_score(risks: list[str]) -> int:
    return sum(RISK_WEIGHTS[risk] for risk in risks)


def baseline_workload(records: list[WeatherRecord], iterations: int) -> dict[str, int]:
    """故意重复解析、排序并保留中间结果，作为优化前基线。"""

    if iterations <= 0:
        raise ValueError("iterations must be positive")
    events: list[tuple[int, int]] = []
    for _ in range(iterations):
        ordered = sorted(records, key=lambda item: datetime.fromisoformat(item.time))
        for record in ordered:
            parsed = datetime.fromisoformat(record.time)
            risks = assess_hour(record.temperature, record.rain_probability, record.wind_speed)
            events.append((parsed.hour * 60 + parsed.minute, _risk_score(risks)))
    return {
        "event_count": len(events),
        "time_checksum": sum(minute for minute, _ in events),
        "risk_score": sum(score for _, score in events),
    }


def optimized_workload(records: list[WeatherRecord], iterations: int) -> dict[str, int]:
    """只解析排序一次，并用累计值代替大中间列表。"""

    if iterations <= 0:
        raise ValueError("iterations must be positive")
    prepared = sorted(
        (
            datetime.fromisoformat(record.time).hour * 60,
            record.temperature,
            record.rain_probability,
            record.wind_speed,
        )
        for record in records
    )
    event_count = 0
    time_checksum = 0
    risk_score = 0
    for _ in range(iterations):
        for minute, temperature, rain_probability, wind_speed in prepared:
            risks = assess_hour(temperature, rain_probability, wind_speed)
            event_count += 1
            time_checksum += minute
            risk_score += _risk_score(risks)
    return {"event_count": event_count, "time_checksum": time_checksum, "risk_score": risk_score}


def measure(
    workload: Callable[[list[WeatherRecord], int], dict[str, int]],
    records: list[WeatherRecord],
    iterations: int,
    *,
    trace_memory: bool,
) -> dict[str, Any]:
    """测量一次工作负载的墙钟时间和可选的 Python 分配峰值。"""

    if trace_memory:
        tracemalloc.start()
    started = time.perf_counter()
    result = workload(records, iterations)
    elapsed = time.perf_counter() - started
    current_bytes = peak_bytes = 0
    if trace_memory:
        current_bytes, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    return {
        "elapsed_seconds": elapsed,
        "current_bytes": current_bytes,
        "peak_bytes": peak_bytes,
        "iterations": iterations,
        "record_count": len(records),
        "result": result,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("baseline", "optimized"), required=True)
    parser.add_argument("--iterations", type=int, default=10_000)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--measure-memory", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    records = load_records(args.data)
    workload = baseline_workload if args.mode == "baseline" else optimized_workload
    metrics = measure(workload, records, args.iterations, trace_memory=args.measure_memory)
    metrics["mode"] = args.mode
    text = json.dumps(metrics, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
