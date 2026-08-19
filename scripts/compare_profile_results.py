"""校验优化前后功能等价，并计算性能变化。"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: compare_profile_results.py BASELINE.json OPTIMIZED.json OUTPUT.json")
    baseline = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    optimized = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    if baseline["result"] != optimized["result"]:
        raise SystemExit("baseline and optimized results differ")
    baseline_time = baseline["elapsed_seconds"]
    optimized_time = optimized["elapsed_seconds"]
    baseline_peak = baseline["peak_bytes"]
    optimized_peak = optimized["peak_bytes"]
    comparison = {
        "equivalent_results": True,
        "speedup": baseline_time / optimized_time,
        "time_reduction_percent": (1 - optimized_time / baseline_time) * 100,
        "peak_memory_reduction_percent": (1 - optimized_peak / baseline_peak) * 100,
        "baseline": baseline,
        "optimized": optimized,
    }
    Path(sys.argv[3]).write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(comparison, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
