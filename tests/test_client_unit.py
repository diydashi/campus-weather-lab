from __future__ import annotations

import json
from urllib.parse import parse_qs, urlparse

import pytest

from campus_weather.client import OpenMeteoClient, ServiceError


def json_transport(payload: object, status: int = 200):
    def transport(url: str, timeout: float) -> tuple[int, bytes]:
        assert timeout == 3.0
        return status, json.dumps(payload).encode("utf-8")

    return transport


def test_search_city_converts_response_to_location() -> None:
    client = OpenMeteoClient(
        timeout=3.0,
        transport=json_transport(
            {"results": [{"name": "南京", "latitude": 32.06, "longitude": 118.79, "country_code": "CN"}]}
        ),
    )

    locations = client.search_city(" 南京 ", count=1)

    assert len(locations) == 1
    assert locations[0].name == "南京"
    assert locations[0].latitude == pytest.approx(32.06)


@pytest.mark.parametrize(
    ("latitude", "longitude", "days", "message"),
    [
        (91, 118.8, 1, "纬度"),
        (32.0, 181, 1, "经度"),
        (32.0, 118.8, 0, "forecast_days"),
        (32.0, 118.8, 17, "forecast_days"),
    ],
)
def test_forecast_rejects_out_of_range_parameters(latitude, longitude, days, message) -> None:
    client = OpenMeteoClient(transport=lambda *_: pytest.fail("非法输入不应发起网络请求"))

    with pytest.raises(ValueError, match=message):
        client.forecast(latitude, longitude, forecast_days=days)


def test_forecast_encodes_required_query_parameters() -> None:
    captured: dict[str, str] = {}

    def transport(url: str, timeout: float) -> tuple[int, bytes]:
        captured["url"] = url
        payload = {
            "hourly": {
                "time": ["2026-08-19T00:00"],
                "temperature_2m": [25.0],
                "precipitation_probability": [10],
                "wind_speed_10m": [5.0],
            }
        }
        return 200, json.dumps(payload).encode("utf-8")

    client = OpenMeteoClient(transport=transport)
    client.forecast(32.06, 118.79, forecast_days=2)

    query = parse_qs(urlparse(captured["url"]).query)
    assert query["forecast_days"] == ["2"]
    assert query["timezone"] == ["Asia/Shanghai"]
    assert set(query["hourly"][0].split(",")) == {
        "temperature_2m",
        "precipitation_probability",
        "wind_speed_10m",
    }


@pytest.mark.parametrize(
    "payload",
    [
        {"results": "not-a-list"},
        {"results": [{"name": "南京", "longitude": 118.79}]},
    ],
)
def test_search_city_rejects_malformed_response(payload) -> None:
    client = OpenMeteoClient(timeout=3.0, transport=json_transport(payload))

    with pytest.raises(ServiceError):
        client.search_city("南京")


def test_http_error_is_exposed_as_service_error() -> None:
    client = OpenMeteoClient(
        timeout=3.0,
        transport=json_transport({"error": True, "reason": "Invalid latitude"}, status=400),
    )

    with pytest.raises(ServiceError, match="HTTP 400.*Invalid latitude"):
        client.search_city("南京")


@pytest.mark.parametrize(
    ("name", "count", "message"),
    [
        ("   ", 5, "城市名不能为空"),
        ("南京", 0, "count"),
        ("南京", 101, "count"),
    ],
)
def test_search_city_rejects_invalid_local_parameters(name, count, message) -> None:
    client = OpenMeteoClient(transport=lambda *_: pytest.fail("非法输入不应发起网络请求"))

    with pytest.raises(ValueError, match=message):
        client.search_city(name, count=count)


@pytest.mark.parametrize(
    "body",
    [b"not-json", b"\xff\xfe"],
)
def test_client_rejects_invalid_json(body) -> None:
    client = OpenMeteoClient(timeout=3.0, transport=lambda *_: (200, body))

    with pytest.raises(ServiceError, match="UTF-8 JSON"):
        client.search_city("南京")


@pytest.mark.parametrize(
    ("hourly", "message"),
    [
        (None, "hourly 对象"),
        ({"time": [], "temperature_2m": [], "precipitation_probability": [], "wind_speed_10m": []}, "数组为空"),
        (
            {
                "time": ["2026-08-19T00:00"],
                "temperature_2m": [25.0, 26.0],
                "precipitation_probability": [10],
                "wind_speed_10m": [5.0],
            },
            "长度不一致",
        ),
        (
            {
                "time": ["2026-08-19T00:00"],
                "temperature_2m": [25.0],
                "precipitation_probability": [10],
            },
            "wind_speed_10m 不是数组",
        ),
    ],
)
def test_forecast_rejects_broken_hourly_contract(hourly, message) -> None:
    client = OpenMeteoClient(timeout=3.0, transport=json_transport({"hourly": hourly}))

    with pytest.raises(ServiceError, match=message):
        client.forecast(32.06, 118.79)
