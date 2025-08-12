import streamlit as st
import pandas as pd
import calendar
from datetime import date
from sqlalchemy import func
from db import SessionLocal, Trainer, Attendance

st.title("Payouts")

year = date.today().year
with SessionLocal() as s:
    trainers = s.query(Trainer).order_by(Trainer.name).all()
names = [t.name for t in trainers]
trainer = st.selectbox("Trainer", names, index=0 if names else None)

quick_split = st.selectbox("Split (trainer %)", ["0.70","0.65","0.60","0.55","0.50"], index=0)
custom_split = st.text_input("Custom split (optional, e.g., 0.68)", "")
effective_split = float(custom_split) if custom_split.strip() else float(quick_split)

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
records = []
for m in range(1, 13):
    rev = monthly.get(m, 0.0)
    payout = rev * effective_split
    gym = rev - payout
    records.append({
        "month": calendar.month_name[m],
        "revenue": round(rev,2),
        "trainer_payout": round(payout,2),
        "gym_retain": round(gym,2),
    })
st.dataframe(pd.DataFrame(records), use_container_width=True)
