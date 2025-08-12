import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import func
from datetime import date
import calendar

from db import SessionLocal, Trainer, Attendance, Config
from utils import project_series

st.title("Dashboard")

with SessionLocal() as s:
    trainers = s.query(Trainer).order_by(Trainer.name).all()
names = [t.name for t in trainers]
trainer = st.selectbox("Trainer", names, index=0 if names else None)

quick_split = st.selectbox("Split (trainer %)", ["0.70","0.65","0.60","0.55","0.50"], index=0)
custom_split = st.text_input("Custom split (optional, e.g., 0.68)", "")
effective_split = float(custom_split) if custom_split.strip() else float(quick_split)

year = date.today().year
current_month = date.today().month

with SessionLocal() as s:
    t = s.query(Trainer).filter(Trainer.name==trainer).first()
    rows = (s.query(
                func.strftime('%m', Attendance.date).label('m'),
                func.sum(Attendance.price_per_session * Attendance.attended).label('revenue')
            )
            .filter(Attendance.trainer_id==t.id)
            .filter(func.strftime('%Y', Attendance.date)==str(year))
            .group_by('m').all())
    monthly = {int(m): float(rev or 0) for (m, rev) in rows}
    ytd_series = [monthly.get(m, 0.0) for m in range(1, current_month+1)]
    cfg = {c.key: c.value for c in s.query(Config).all()}
    months_ahead = int(cfg.get("projection_months_ahead","6"))
    retention = float(cfg.get("default_retention_rate","0.92"))
    growth = float(cfg.get("default_growth_rate","0.05"))

projection = project_series(ytd_series, months_ahead, retention, growth)

this_month_rev = ytd_series[-1] if ytd_series else 0.0
this_month_payout = this_month_rev * effective_split
this_month_gym = this_month_rev - this_month_payout
ytd_rev = sum(ytd_series)
ytd_payout = ytd_rev * effective_split
ytd_gym = ytd_rev - ytd_payout

c1, c2, c3 = st.columns(3)
c1.metric("This Month Revenue", f"${this_month_rev:,.0f}")
c2.metric("Trainer Payout", f"${this_month_payout:,.0f}")
c3.metric("Gym Retain", f"${this_month_gym:,.0f}")

c4, c5, c6 = st.columns(3)
c4.metric("YTD Revenue", f"${ytd_rev:,.0f}")
c5.metric("YTD Trainer Payout", f"${ytd_payout:,.0f}")
c6.metric("YTD Gym Retain", f"${ytd_gym:,.0f}")

fig = plt.figure(figsize=(10,4))
months = list(range(1,13))
plt.plot(list(range(1, len(ytd_series)+1)), ytd_series, label="Actual YTD")
proj_x = list(range(current_month+1, current_month+1+len(projection)))
plt.plot(proj_x, projection, linestyle="--", linewidth=1, label="Projection")
plt.xticks(range(1,13), [calendar.month_abbr[m] for m in range(1,13)])
plt.xlabel("Month"); plt.ylabel("Revenue ($)")
plt.title(f"YTD Revenue & Projection – {trainer}")
plt.legend()
st.pyplot(fig)
