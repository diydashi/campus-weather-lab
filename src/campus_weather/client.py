"""Open-Meteo REST API 的轻量客户端。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class ServiceError(RuntimeError):
    """远程服务请求失败或返回不符合约定的数据。"""


Transport = Callable[[str, float], tuple[int, bytes]]


@dataclass(frozen=True)
class Location:
    """地理编码服务返回的位置。"""

    name: str
    latitude: float
    longitude: float
    country_code: str | None = None


def _default_transport(url: str, timeout: float) -> tuple[int, bytes]:
    request = Request(url, headers={"User-Agent": "campus-weather-lab/0.1"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, response.read()
    except HTTPError as exc:
        return exc.code, exc.read()
    except (URLError, TimeoutError, OSError) as exc:
        raise ServiceError(f"无法访问远程服务: {exc}") from exc


class OpenMeteoClient:
    """访问 Open-Meteo 地理编码和天气预报接口。"""

    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(
        self,
        *,
        timeout: float = 10.0,
        transport: Transport | None = None,
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout 必须大于 0")
        self.timeout = timeout
        self._transport = transport or _default_transport

    def _get_json(self, base_url: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{base_url}?{urlencode(params)}"
        status, body = self._transport(url, self.timeout)
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ServiceError("远程服务返回的不是有效 UTF-8 JSON") from exc
        if status != 200:
            reason = payload.get("reason", "未知原因") if isinstance(payload, dict) else "未知原因"
            raise ServiceError(f"远程服务返回 HTTP {status}: {reason}")
        if not isinstance(payload, dict):
            raise ServiceError("远程服务 JSON 顶层不是对象")
        return payload

    def search_city(self, name: str, *, count: int = 5) -> list[Location]:
        """按城市名搜索位置；无结果时返回空列表。"""

        if not name.strip():
            raise ValueError("城市名不能为空")
        if not 1 <= count <= 100:
            raise ValueError("count 必须在 1 到 100 之间")
        payload = self._get_json(
            self.GEOCODING_URL,
            {"name": name.strip(), "count": count, "language": "zh", "format": "json"},
        )
        results = payload.get("results", [])
        if not isinstance(results, list):
            raise ServiceError("地理编码响应中的 results 不是数组")
        locations: list[Location] = []
        for item in results:
            try:
                locations.append(
                    Location(
                        name=str(item["name"]),
                        latitude=float(item["latitude"]),
                        longitude=float(item["longitude"]),
                        country_code=item.get("country_code"),
                    )
                )
            except (KeyError, TypeError, ValueError) as exc:
                raise ServiceError("地理编码响应缺少合法的位置字段") from exc
        return locations

    def forecast(self, latitude: float, longitude: float, *, forecast_days: int = 1) -> dict[str, Any]:
        """获取小时温度、降水概率和风速数据。"""

        if not -90 <= latitude <= 90:
            raise ValueError("纬度必须在 -90 到 90 之间")
        if not -180 <= longitude <= 180:
            raise ValueError("经度必须在 -180 到 180 之间")
        if not 1 <= forecast_days <= 16:
            raise ValueError("forecast_days 必须在 1 到 16 之间")
        payload = self._get_json(
            self.FORECAST_URL,
            {
                "latitude": latitude,
                "longitude": longitude,
                "hourly": "temperature_2m,precipitation_probability,wind_speed_10m",
                "forecast_days": forecast_days,
                "timezone": "Asia/Shanghai",
            },
        )
        self._validate_hourly_forecast(payload)
        return payload

    @staticmethod
    def _validate_hourly_forecast(payload: dict[str, Any]) -> None:
        """检查项目依赖的小时预报契约，尽早暴露接口结构变化。"""

        hourly = payload.get("hourly")
        if not isinstance(hourly, dict):
            raise ServiceError("天气响应缺少 hourly 对象")

        required_series = (
            "time",
            "temperature_2m",
            "precipitation_probability",
            "wind_speed_10m",
        )
        series_lengths: set[int] = set()
        for field in required_series:
            values = hourly.get(field)
            if not isinstance(values, list):
                raise ServiceError(f"天气响应中的 {field} 不是数组")
            series_lengths.add(len(values))

        if series_lengths == {0}:
            raise ServiceError("天气响应中的小时数组为空")
        if len(series_lengths) != 1:
            raise ServiceError("天气响应中的小时数组长度不一致")
