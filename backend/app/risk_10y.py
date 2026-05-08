from __future__ import annotations

import math

from .models import RiskInput, RiskValue

MMOL_FACTOR = 0.0259


def to_mg_dl(value: float, unit: int) -> float:
    return value if unit == 1 else value / MMOL_FACTOR


def calculate_ten_year_risk(payload: RiskInput) -> RiskValue:
    age = math.log(payload.age)
    sbp = math.log(payload.sbp)
    tc = math.log(to_mg_dl(payload.tc, payload.tc_unit))
    hdlc = math.log(to_mg_dl(payload.hdlc, payload.hdlc_unit))
    waist = math.log(payload.waist)
    treated_sbp = sbp if payload.drug == 1 else 0.0
    untreated_sbp = sbp if payload.drug == 0 else 0.0
    age_treated = age * treated_sbp
    age_untreated = age * untreated_sbp

    if payload.sex == 1:
        z = (
            32.344877 * age
            + 27.704396 * treated_sbp
            + 26.455809 * untreated_sbp
            + 0.619958 * tc
            - 0.700506 * hdlc
            - 0.717373 * waist
            + 3.976209 * payload.csmoke
            + 0.356826 * payload.dm
            + 0.478726 * payload.region
            - 0.162623 * payload.area
            + 6.228884 * payload.fh_ascvd
            - 6.093602 * age_treated
            - 5.804677 * age_untreated
            - 0.943908 * age * payload.csmoke
            - 1.536263 * age * payload.fh_ascvd
            - 145.726914
        )
    else:
        z = (
            25.266747 * age
            + 21.036129 * treated_sbp
            + 20.290294 * untreated_sbp
            + 0.064764 * tc
            - 0.212145 * hdlc
            + 1.469891 * waist
            + 0.496938 * payload.csmoke
            + 0.570571 * payload.dm
            + 0.545760 * payload.region
            - 4.609343 * age_treated
            - 4.436694 * age_untreated
            - 123.071553
        )

    percent = (1 - math.exp(-math.exp(z))) * 100
    return RiskValue.from_percent(percent)
