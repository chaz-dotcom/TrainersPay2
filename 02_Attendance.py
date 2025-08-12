import streamlit as st
import pandas as pd
from datetime import date
from sqlalchemy import select
from db import SessionLocal, Attendance, Trainer, Client

st.title("Attendance")

with SessionLocal() as s:
    trainers = s.query(Trainer).order_by(Trainer.name).all()
    clients = s.query(Client).order_by(Client.name).all()

trainer_map = {t.name: t.id for t in trainers}
client_map = {c.name: c.id for c in clients}

with st.form("attendance_form", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    d = c1.date_input("Date", value=date.today())
    trainer_name = c2.selectbox("Trainer", list(trainer_map.keys()))
    client_name = c3.selectbox("Client", list(client_map.keys()))
    c4, c5, c6 = st.columns(3)
    session_length = c4.number_input("Session length (min)", min_value=15, max_value=120, value=60, step=15)
    price = c5.number_input("Price per session ($)", min_value=0.0, value=80.0, step=5.0, format="%.2f")
    attended = c6.selectbox("Status", ["Attended","No-show/Cancel"], index=0)
    notes = st.text_input("Notes", "")
    submitted = st.form_submit_button("Add Session")
    if submitted:
        with SessionLocal() as s:
            s.add(Attendance(
                date=d, trainer_id=trainer_map[trainer_name], client_id=client_map[client_name],
                session_length_min=int(session_length), price_per_session=float(price),
                attended=1 if attended=="Attended" else 0, notes=notes
            ))
            s.commit()
        st.success("Session logged.")

st.subheader("Recent Sessions")
with SessionLocal() as s:
    rows = s.execute(select(Attendance)).scalars().all()
df = pd.DataFrame([{
    "date": a.date, "trainer_id": a.trainer_id, "client_id": a.client_id,
    "session_length_min": a.session_length_min, "price_per_session": a.price_per_session,
    "attended": a.attended, "notes": a.notes
} for a in rows])
if not df.empty:
    with SessionLocal() as s:
        tmap = {t.id: t.name for t in s.query(Trainer).all()}
        cmap = {c.id: c.name for c in s.query(Client).all()}
    df["trainer"] = df["trainer_id"].map(tmap)
    df["client"] = df["client_id"].map(cmap)
    df = df[["date","trainer","client","session_length_min","price_per_session","attended","notes"]]
st.dataframe(df, use_container_width=True)
