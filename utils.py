import calendar
from datetime import date, datetime
import numpy as np

def month_abbr(m: int) -> str:
    return calendar.month_abbr[m]

def month_name(m: int) -> str:
    return calendar.month_name[m]

def ymd(d):
    if isinstance(d, (date, datetime)):
        return d.strftime("%Y-%m-%d")
    return str(d)

def project_series(actual_series, months_ahead: int, retention: float, growth: float):
    if len(actual_series) >= 3:
        baseline = float(np.mean(actual_series[-3:]))
    elif len(actual_series) >= 1:
        baseline = float(np.mean(actual_series))
    else:
        baseline = 0.0
    projections = []
    current = baseline
    for _ in range(months_ahead):
        current = current * retention * (1.0 + growth)
        projections.append(round(float(current), 2))
    return projections
