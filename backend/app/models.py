from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class RiskInput:
    sex: int
    age: int
    region: int
    area: int
    waist: float
    tc_unit: int
    tc: float
    hdlc_unit: int
    hdlc: float
    sbp: int
    dbp: int
    drug: int
    dm: int
    csmoke: int
    fh_ascvd: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class RiskValue:
    value: float
    percent: float
    level: str | None = None

    @classmethod
    def from_percent(cls, percent: float, level: str | None = None) -> "RiskValue":
        return cls(value=percent / 100.0, percent=round(percent, 1), level=level)

    def to_dict(self) -> dict:
        return {"value": self.value, "percent": self.percent, "level": self.level}
