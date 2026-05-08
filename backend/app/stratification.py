def stratify_ten_year(percent: float) -> str:
    if percent < 5:
        return "低危"
    if percent < 10:
        return "中危"
    return "高危"


def stratify_lifetime(percent: float) -> str:
    return "低危" if percent < 32.8 else "高危"
