"""可离线测试的校园出行风险规则。"""

from __future__ import annotations


def assess_hour(temperature: float, precipitation_probability: float, wind_speed: float) -> list[str]:
    """根据单小时天气指标给出确定性的出行提示。"""

    if not -100 <= temperature <= 70:
        raise ValueError("温度超出可接受范围")
    if not 0 <= precipitation_probability <= 100:
        raise ValueError("降水概率必须在 0 到 100 之间")
    if wind_speed < 0:
        raise ValueError("风速不能为负数")

    risks: list[str] = []
    if temperature >= 35:
        risks.append("高温")
    elif temperature <= 0:
        risks.append("低温")
    if precipitation_probability >= 60:
        risks.append("建议带伞")
    if wind_speed >= 40:
        risks.append("注意大风")
    return risks or ["适宜出行"]

