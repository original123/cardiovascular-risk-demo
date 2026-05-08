from __future__ import annotations

from dataclasses import replace

from .models import RiskInput


def build_ideal_input(payload: RiskInput) -> RiskInput:
    return replace(
        payload,
        waist=90.0 if payload.sex == 1 else 85.0,
        tc_unit=1,
        tc=200.0,
        hdlc_unit=1,
        hdlc=40.0,
        sbp=120,
        dbp=80,
        drug=0,
        dm=0,
        csmoke=0,
        fh_ascvd=0,
    )
