import streamlit as st
import pandas as pd
from datetime import date
from sqlalchemy import select
from db import SessionLocal, Agreement, Trainer, Client

st.title("Agreements")

with SessionLocal() as s:
    trainers = s.query(Trainer).order_by(Trainer.name).all()
    clients = s.query(Client).order_by(Client.name).all()

trainer_map = {t.name: t.id for t in trainers}
client_map = {c.name: c.id for c in clients}

with st.form("agreement_form", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    client_name = c1.selectbox("Client", list(client_map.keys()))
    trainer_name = c2.selectbox("Trainer", list(trainer_map.keys()))
    start_date = c3.date_input("Start date", value=date(date.today().year, 1, 1))
    c4, c5 = st.columns(2)
    session_length = c4.number_input("Session length (min)", min_value=15, max_value=120, value=60, step=15)
    price = c5.number_input("Price per session ($)", min_value=0.0, value=80.0, step=5.0, format="%.2f")
    submitted = st.form_submit_button("Add Agreement")
    if submitted:
        with SessionLocal() as s:
            s.add(Agreement(client_id=client_map[client_name], trainer_id=trainer_map[trainer_name],
                            start_date=start_date, session_length_min=int(session_length),
                            price_per_session=float(price)))
            s.commit()
        st.success("Agreement added.")

st.subheader("Existing Agreements")
with SessionLocal() as s:
    rows = s.execute(select(Agreement)).scalars().all()
df = pd.DataFrame([{
    "id": a.id, "client_id": a.client_id, "trainer_id": a.trainer_id,
    "start_date": a.start_date, "end_date": a.end_date,
    "session_length_min": a.session_length_min, "price_per_session": a.price_per_session
} for a in rows])
if not df.empty:
    with SessionLocal() as s:
        tmap = {t.id: t.name for t in s.query(Trainer).all()}
        cmap = {c.id: c.name for c in s.query(Client).all()}
    df["trainer"] = df["trainer_id"].map(tmap)
    df["client"] = df["client_id"].map(cmap)
    df = df[["id","client","trainer","start_date","end_date","session_length_min","price_per_session"]]
st.dataframe(df, use_container_width=True)
