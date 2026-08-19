"""把 cProfile 二进制结果转换为便于阅读的文本。"""

from __future__ import annotations

import pstats
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: summarize_profile.py INPUT.prof OUTPUT.txt")
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as stream:
        stats = pstats.Stats(str(input_path), stream=stream)
        stats.strip_dirs().sort_stats("cumulative").print_stats(20)


if __name__ == "__main__":
    main()
