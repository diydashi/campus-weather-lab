"""校园出行天气风险分析工具。"""

from .client import OpenMeteoClient, ServiceError
from .risk import assess_hour

__all__ = ["OpenMeteoClient", "ServiceError", "assess_hour"]

