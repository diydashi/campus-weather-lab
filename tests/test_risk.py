import pytest

from campus_weather.risk import assess_hour


@pytest.mark.parametrize(
    ("temperature", "rain", "wind", "expected"),
    [
        (25, 10, 5, ["适宜出行"]),
        (36, 10, 5, ["高温"]),
        (-1, 80, 5, ["低温", "建议带伞"]),
        (25, 80, 45, ["建议带伞", "注意大风"]),
    ],
)
def test_assess_hour_is_parameterized(temperature, rain, wind, expected) -> None:
    assert assess_hour(temperature, rain, wind) == expected


@pytest.mark.parametrize("rain", [-1, 101])
def test_assess_hour_rejects_invalid_probability(rain) -> None:
    with pytest.raises(ValueError, match="降水概率"):
        assess_hour(20, rain, 10)

