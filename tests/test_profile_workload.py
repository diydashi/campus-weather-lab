from pathlib import Path

import pytest

from benchmarks.profile_workload import baseline_workload, load_records, optimized_workload


PROJECT_ROOT = Path(__file__).parents[1]


def test_fixed_profile_dataset_has_aligned_24_hours() -> None:
    records = load_records(PROJECT_ROOT / "data" / "sample_weather.json")

    assert len(records) == 24
    assert records[0].time == "2026-08-19T00:00"
    assert records[-1].time == "2026-08-19T23:00"


@pytest.mark.parametrize("iterations", [1, 3])
def test_optimized_workload_preserves_baseline_result(iterations) -> None:
    records = load_records(PROJECT_ROOT / "data" / "sample_weather.json")

    assert optimized_workload(records, iterations) == baseline_workload(records, iterations)


@pytest.mark.parametrize("workload", [baseline_workload, optimized_workload])
def test_workloads_reject_non_positive_iterations(workload) -> None:
    records = load_records(PROJECT_ROOT / "data" / "sample_weather.json")

    with pytest.raises(ValueError, match="positive"):
        workload(records, 0)
