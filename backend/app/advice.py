from __future__ import annotations

from .models import RiskInput


BASE_ADVICE = {
    "低危": "应该接受生活方式指导，以保持自身的低风险状况，加强自我监测。",
    "中危": "应积极改变不良生活方式，如戒烟、控制体重、增加体力活动等，如有必要可以在临床医生指导下进行相关治疗。",
    "高危": "应积极改变不良生活方式，如戒烟、控制体重、增加体力活动等，同时应该针对自身危险因素，在临床医生指导下进行降压、调脂、降糖等药物治疗。至少每年进行一次体检，必要时可以进行心脏超声、颈动脉超声等详细的影像学检查，以进一步评估心脑血管病风险。",
}


def build_advice(
    payload: RiskInput,
    ten_year_level: str,
    lifetime_level: str | None = None,
) -> list[str]:
    advice = [BASE_ADVICE[ten_year_level]]

    if payload.age < 60 and ten_year_level != "高危" and lifetime_level == "高危":
        advice.append("鉴于您终生风险处于高危水平，请密切注意相关危险因素，采取必要干预措施。")

    if (payload.sex == 1 and payload.waist >= 90) or (payload.sex == 2 and payload.waist >= 85):
        advice.append("您为中心型肥胖，应积极改变生活方式，控制体重和腰围。")

    if payload.sbp >= 140 or payload.dbp >= 90:
        if payload.drug == 1:
            advice.append("您血压控制不佳，应咨询专业医师，进一步采取措施，控制血压。")
        else:
            advice.append("您为高血压，应密切关注血压，必要时就医，进行治疗。")

    tc_mg_dl = payload.tc if payload.tc_unit == 1 else payload.tc / 0.0259
    if tc_mg_dl >= 240:
        advice.append("您为高胆固醇血症，应密切关注总胆固醇水平，必要时就医，进行治疗。")

    if payload.dm == 1:
        advice.append("请积极治疗糖尿病，避免并发症的发生。")

    if payload.csmoke == 1:
        advice.append("吸烟是心脑血管病的重要危险因素，建议立即戒烟。")

    return advice
