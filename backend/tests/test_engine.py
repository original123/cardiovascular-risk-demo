import math

import pytest

from app.advice import build_advice
from app.ideal import build_ideal_input
from app.risk_10y import calculate_ten_year_risk, to_mg_dl
from app.service import evaluate
from app.stratification import stratify_lifetime, stratify_ten_year
from app.validation import ValidationError, validate_payload


GUIDE_SAMPLE = {
    "sex": 1,
    "age": 40,
    "region": 1,
    "area": 1,
    "waist": 80,
    "tc_unit": 2,
    "tc": 5.2,
    "hdlc_unit": 2,
    "hdlc": 1.3,
    "sbp": 145,
    "dbp": 80,
    "drug": 0,
    "dm": 0,
    "csmoke": 0,
    "fh_ascvd": 1,
}


IDEAL_SAMPLE = {
    "sex": 1,
    "age": 40,
    "region": 1,
    "area": 1,
    "waist": 90,
    "tc_unit": 1,
    "tc": 200,
    "hdlc_unit": 1,
    "hdlc": 40,
    "sbp": 120,
    "dbp": 80,
    "drug": 0,
    "dm": 0,
    "csmoke": 0,
    "fh_ascvd": 0,
}


def assert_percent_close(actual, expected, tolerance=0.15):
    assert abs(actual - expected) <= tolerance


def test_unit_conversion_uses_official_factor():
    assert to_mg_dl(5.2, 2) == pytest.approx(200.7722, rel=1e-5)
    assert to_mg_dl(180, 1) == 180


def test_guide_sample_matches_official_ten_year_result():
    payload = validate_payload(GUIDE_SAMPLE)
    risk = calculate_ten_year_risk(payload)
    assert_percent_close(risk.percent, 4.7)


def test_evaluate_guide_sample_returns_expected_result_and_advice():
    result = evaluate(GUIDE_SAMPLE)
    assert_percent_close(result["tenYearRisk"]["percent"], 4.7)
    assert_percent_close(result["idealTenYearRisk"]["percent"], 1.1)
    assert_percent_close(result["lifetimeRisk"]["percent"], 37.8, tolerance=5.0)
    assert_percent_close(result["idealLifetimeRisk"]["percent"], 20.7, tolerance=5.0)
    assert result["tenYearRisk"]["level"] == "低危"
    assert result["lifetimeRisk"]["level"] == "高危"
    assert any("终生风险处于高危水平" in item for item in result["advice"])
    assert any("高血压" in item for item in result["advice"])


def test_ideal_input_uses_threshold_values_and_matches_actual_risk():
    payload = validate_payload(IDEAL_SAMPLE)
    ideal = build_ideal_input(payload)
    assert ideal.tc == 200
    assert ideal.hdlc == 40
    assert ideal.sbp == 120
    assert ideal.dbp == 80
    assert ideal.waist == 90
    result = evaluate(IDEAL_SAMPLE)
    assert result["tenYearRisk"]["percent"] == result["idealTenYearRisk"]["percent"]
    assert result["lifetimeRisk"]["percent"] == result["idealLifetimeRisk"]["percent"]


@pytest.mark.parametrize(
    ("risk", "expected"),
    [(4.999, "低危"), (5.0, "中危"), (9.999, "中危"), (10.0, "高危")],
)
def test_ten_year_stratification_boundaries(risk, expected):
    assert stratify_ten_year(risk) == expected


@pytest.mark.parametrize(
    ("risk", "expected"),
    [(32.799, "低危"), (32.8, "高危")],
)
def test_lifetime_stratification_boundaries(risk, expected):
    assert stratify_lifetime(risk) == expected


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"waist": 90}, "中心型肥胖"),
        ({"sbp": 140}, "高血压"),
        ({"drug": 1, "sbp": 140}, "血压控制不佳"),
        ({"tc_unit": 1, "tc": 240}, "高胆固醇血症"),
        ({"dm": 1}, "糖尿病"),
        ({"csmoke": 1}, "戒烟"),
    ],
)
def test_advice_triggers_for_single_risk_factors(changes, message):
    data = {**IDEAL_SAMPLE, **changes}
    payload = validate_payload(data)
    advice = build_advice(payload, ten_year_level="低危", lifetime_level="低危")
    assert any(message in item for item in advice)


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({}, "评测项不得为空"),
        ({"age": 19}, "年龄应在20-85之间"),
        ({"age": 20.5}, "评测项不得为空"),
        ({"sbp": 115.5}, "评测项不得为空"),
        ({"waist": 80.5}, None),
        ({"tc": 180.5}, None),
        ({"sex": 9}, "性别不在给定范围内"),
    ],
)
def test_validation_rules(changes, message):
    data = dict(IDEAL_SAMPLE)
    if changes:
        data.update(changes)
    else:
        data.pop("sex")

    if message is None:
        assert validate_payload(data)
        return

    with pytest.raises(ValidationError) as exc:
        validate_payload(data)
    assert message in str(exc.value)


def test_age_sixty_hides_lifetime_risk():
    result = evaluate({**IDEAL_SAMPLE, "age": 60})
    assert result["lifetimeRisk"] is None
    assert result["idealLifetimeRisk"] is None
    assert "60岁以下" in result["lifetimeRiskNote"]
