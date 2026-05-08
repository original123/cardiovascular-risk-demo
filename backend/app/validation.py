from __future__ import annotations

from typing import Any

from .models import RiskInput


class ValidationError(ValueError):
    pass


REQUIRED_FIELDS = (
    "sex",
    "age",
    "region",
    "area",
    "waist",
    "tc_unit",
    "tc",
    "hdlc_unit",
    "hdlc",
    "sbp",
    "dbp",
    "drug",
    "dm",
    "csmoke",
    "fh_ascvd",
)


def _is_empty(value: Any) -> bool:
    return value is None or value == ""


def _parse_int(value: Any) -> int:
    if isinstance(value, bool):
        raise ValidationError("评测项不得为空")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    raise ValidationError("评测项不得为空")


def _parse_number(value: Any) -> float:
    if isinstance(value, bool):
        raise ValidationError("评测项不得为空")
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValidationError("评测项不得为空") from None


def _require_enum(name: str, value: int, allowed: set[int], message: str) -> None:
    if value not in allowed:
        raise ValidationError(message)


def _range(value: float, low: float, high: float, message: str) -> None:
    if value < low or value > high:
        raise ValidationError(message)


def validate_payload(payload: dict[str, Any]) -> RiskInput:
    for field in REQUIRED_FIELDS:
        if field not in payload or _is_empty(payload[field]):
            raise ValidationError("评测项不得为空")

    sex = _parse_int(payload["sex"])
    age = _parse_int(payload["age"])
    region = _parse_int(payload["region"])
    area = _parse_int(payload["area"])
    waist = _parse_number(payload["waist"])
    tc_unit = _parse_int(payload["tc_unit"])
    tc = _parse_number(payload["tc"])
    hdlc_unit = _parse_int(payload["hdlc_unit"])
    hdlc = _parse_number(payload["hdlc"])
    sbp = _parse_int(payload["sbp"])
    dbp = _parse_int(payload["dbp"])
    drug = _parse_int(payload["drug"])
    dm = _parse_int(payload["dm"])
    csmoke = _parse_int(payload["csmoke"])
    fh_ascvd = _parse_int(payload["fh_ascvd"])

    _require_enum("sex", sex, {1, 2}, "性别不在给定范围内")
    _require_enum("region", region, {0, 1}, "现住址地区不在给定范围内")
    _require_enum("area", area, {0, 1}, "现住址地区不在给定范围内")
    _require_enum("tc_unit", tc_unit, {1, 2}, "总胆固醇单位不在给定范围内")
    _require_enum("hdlc_unit", hdlc_unit, {1, 2}, "高密度脂蛋白胆固醇单位不在给定范围内")
    _require_enum("drug", drug, {0, 1}, "服用降压药不在给定范围内")
    _require_enum("dm", dm, {0, 1}, "患糖尿病不在给定范围内")
    _require_enum("csmoke", csmoke, {0, 1}, "现在是否吸烟不在给定范围内")
    _require_enum("fh_ascvd", fh_ascvd, {0, 1}, "心脑血管病家族史不在给定范围内")

    _range(age, 20, 85, "年龄应在20-85之间")
    _range(waist, 50, 130, "腰围应在50-130之间")
    if tc_unit == 1:
        _range(tc, 80, 400, "总胆固醇应在80-400mg/dl之间")
    else:
        _range(tc, 2, 11, "总胆固醇应在2-11mmol/L之间")
    if hdlc_unit == 1:
        _range(hdlc, 20, 130, "高密度脂蛋白胆固醇应在20-130mg/dl之间")
    else:
        _range(hdlc, 0.5, 4, "高密度脂蛋白胆固醇应在0.5-4mmol/L之间")
    _range(sbp, 70, 200, "收缩压应在70-200之间")
    _range(dbp, 40, 140, "舒张压应在40-140之间")

    return RiskInput(
        sex=sex,
        age=age,
        region=region,
        area=area,
        waist=waist,
        tc_unit=tc_unit,
        tc=tc,
        hdlc_unit=hdlc_unit,
        hdlc=hdlc,
        sbp=sbp,
        dbp=dbp,
        drug=drug,
        dm=dm,
        csmoke=csmoke,
        fh_ascvd=fh_ascvd,
    )
