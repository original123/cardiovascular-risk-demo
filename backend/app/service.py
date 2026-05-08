from __future__ import annotations

from .advice import build_advice
from .ideal import build_ideal_input
from .lifetime import LIFETIME_MODEL_INFO, calculate_lifetime_risk
from .risk_10y import calculate_ten_year_risk
from .stratification import stratify_lifetime, stratify_ten_year
from .validation import validate_payload

TEN_YEAR_MODEL_INFO = {
    "type": "china_par_10y_black_box_fit",
    "source": "China-PAR Circulation 2016 structure + cvdrisk.com.cn fitted coefficients",
    "warning": "工程拟合结果，用于复刻官网展示值",
}


def _with_level(risk, level: str):
    return {"value": risk.value, "percent": risk.percent, "level": level}


def evaluate(payload: dict) -> dict:
    risk_input = validate_payload(payload)
    ideal_input = build_ideal_input(risk_input)

    ten_year = calculate_ten_year_risk(risk_input)
    ideal_ten_year = calculate_ten_year_risk(ideal_input)
    ten_year_level = stratify_ten_year(ten_year.percent)

    lifetime = calculate_lifetime_risk(risk_input)
    ideal_lifetime = calculate_lifetime_risk(ideal_input)
    lifetime_level = stratify_lifetime(lifetime.percent) if lifetime else None

    advice = build_advice(risk_input, ten_year_level, lifetime_level)

    return {
        "input": risk_input.to_dict(),
        "tenYearRisk": _with_level(ten_year, ten_year_level),
        "idealTenYearRisk": _with_level(
            ideal_ten_year,
            stratify_ten_year(ideal_ten_year.percent),
        ),
        "lifetimeRisk": _with_level(lifetime, lifetime_level) if lifetime else None,
        "idealLifetimeRisk": (
            _with_level(ideal_lifetime, stratify_lifetime(ideal_lifetime.percent))
            if ideal_lifetime
            else None
        ),
        "lifetimeRiskNote": "终生风险只在60岁以下人群中计算。" if not lifetime else "",
        "advice": advice,
        "models": {
            "tenYearRisk": TEN_YEAR_MODEL_INFO,
            "lifetimeRisk": LIFETIME_MODEL_INFO,
        },
    }
