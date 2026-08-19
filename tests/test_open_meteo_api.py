from __future__ import annotations

import pytest

from campus_weather.client import OpenMeteoClient


pytestmark = pytest.mark.network


@pytest.fixture(scope="module")
def client() -> OpenMeteoClient:
    return OpenMeteoClient(timeout=15.0)


@pytest.mark.parametrize(
    ("city", "expected_country"),
    [("南京", "CN"), ("北京", "CN"), ("上海", "CN")],
)
def test_geocoding_returns_plausible_chinese_city(client, city, expected_country) -> None:
    locations = client.search_city(city, count=5)

    assert locations, f"{city} 应至少返回一个候选位置"
    assert any(location.country_code == expected_country for location in locations)
    for location in locations:
        assert -90 <= location.latitude <= 90
        assert -180 <= location.longitude <= 180


def test_unknown_city_returns_empty_result(client) -> None:
    assert client.search_city("zzzzzz-no-such-campus-city-987654") == []


@pytest.mark.parametrize("forecast_days", [1, 2])
def test_forecast_has_aligned_hourly_series(client, forecast_days) -> None:
    payload = client.forecast(32.06, 118.79, forecast_days=forecast_days)
    hourly = payload["hourly"]
    expected_length = forecast_days * 24

    assert payload["timezone"] == "Asia/Shanghai"
    assert payload["utc_offset_seconds"] == 8 * 60 * 60
    assert payload["latitude"] == pytest.approx(32.06, abs=0.2)
    assert payload["longitude"] == pytest.approx(118.79, abs=0.2)
    assert len(hourly["time"]) == expected_length
    assert len(hourly["temperature_2m"]) == expected_length
    assert len(hourly["precipitation_probability"]) == expected_length
    assert len(hourly["wind_speed_10m"]) == expected_length
    assert all(-100 <= value <= 70 for value in hourly["temperature_2m"])
    assert all(value is None or 0 <= value <= 100 for value in hourly["precipitation_probability"])
    assert all(value >= 0 for value in hourly["wind_speed_10m"])


def test_forecast_reports_requested_units(client) -> None:
    payload = client.forecast(32.06, 118.79)

    assert payload["hourly_units"] == {
        "time": "iso8601",
        "temperature_2m": "°C",
        "precipitation_probability": "%",
        "wind_speed_10m": "km/h",
    }
