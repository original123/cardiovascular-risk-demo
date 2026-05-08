from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

from .models import RiskInput, RiskValue
from .risk_10y import to_mg_dl

MODEL_PATH = Path(__file__).resolve().parents[2] / "docs" / "research" / "lifetime_poly2_model.json"


def _sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1 / (1 + z)
    z = math.exp(x)
    return z / (1 + z)


@lru_cache(maxsize=1)
def load_model() -> dict:
    with MODEL_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def _base_features(payload: RiskInput) -> list[float]:
    age = float(payload.age)
    sbp = math.log(payload.sbp)
    tc = math.log(to_mg_dl(payload.tc, payload.tc_unit))
    hdlc = math.log(to_mg_dl(payload.hdlc, payload.hdlc_unit))
    waist = math.log(payload.waist)
    drug = float(payload.drug)
    return [
        age,
        age * age,
        math.log(age),
        sbp,
        tc,
        hdlc,
        waist,
        drug,
        float(payload.csmoke),
        float(payload.dm),
        float(payload.region),
        float(payload.area),
        float(payload.fh_ascvd),
        drug * sbp,
        (1 - drug) * sbp,
    ]


def _poly2(normalized: list[float]) -> list[float]:
    features = [1.0, *normalized]
    for i in range(len(normalized)):
        for j in range(i, len(normalized)):
            features.append(normalized[i] * normalized[j])
    return features


def calculate_lifetime_risk(payload: RiskInput) -> RiskValue | None:
    if payload.age >= 60:
        return None

    model = load_model()
    sex_model = next(item for item in model["models"] if item["sex"] == payload.sex)
    base = _base_features(payload)
    normalized = [
        (value - sex_model["mean"][idx]) / sex_model["sd"][idx]
        for idx, value in enumerate(base)
    ]
    features = _poly2(normalized)
    z = sum(coef * value for coef, value in zip(sex_model["coef"], features))
    percent = _sigmoid(z) * 100
    return RiskValue.from_percent(percent)


LIFETIME_MODEL_INFO = {
    "type": "black_box_poly2_approximation",
    "source": "cvdrisk.com.cn black-box fit",
    "warning": "工程拟合结果，非原始 China-PAR 终生风险公式",
}
