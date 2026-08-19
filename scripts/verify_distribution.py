"""检查 wheel 和 sdist 是否包含项目的关键源码。"""

from __future__ import annotations

import sys
import tarfile
import zipfile
from pathlib import Path


def main() -> None:
    dist_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist")
    wheels = sorted(dist_dir.glob("*.whl"))
    sdists = sorted(dist_dir.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise SystemExit(f"expected one wheel and one sdist, got {wheels!r} and {sdists!r}")

    with zipfile.ZipFile(wheels[0]) as archive:
        wheel_names = set(archive.namelist())
    if "campus_weather/client.py" not in wheel_names or "campus_weather/risk.py" not in wheel_names:
        raise SystemExit("wheel is missing campus_weather source files")

    with tarfile.open(sdists[0], "r:gz") as archive:
        sdist_names = set(archive.getnames())
    if not any(name.endswith("src/campus_weather/client.py") for name in sdist_names):
        raise SystemExit("sdist is missing client.py")

    print(f"verified wheel: {wheels[0].name}")
    print(f"verified sdist: {sdists[0].name}")


if __name__ == "__main__":
    main()
