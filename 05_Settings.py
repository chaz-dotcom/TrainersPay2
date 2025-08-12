import streamlit as st
from db import SessionLocal, Config, Trainer

st.title("Settings")

with SessionLocal() as s:
    cfg_rows = {c.key: c for c in s.query(Config).all()}
    retention = float(cfg_rows.get("default_retention_rate", Config(key="default_retention_rate", value="0.92")).value)
    growth = float(cfg_rows.get("default_growth_rate", Config(key="default_growth_rate", value="0.05")).value)
    months_ahead = int(cfg_rows.get("projection_months_ahead", Config(key="projection_months_ahead", value="6")).value)

retention = st.number_input("Default retention rate", min_value=0.0, max_value=1.0, value=retention, step=0.01)
growth = st.number_input("Default monthly growth", min_value=0.0, max_value=1.0, value=growth, step=0.01)
months_ahead = st.number_input("Projection months ahead", min_value=1, max_value=24, value=months_ahead, step=1)

if st.button("Save config"):
    with SessionLocal() as s:
        for k, v in [
            ("default_retention_rate", str(retention)),
            ("default_growth_rate", str(growth)),
            ("projection_months_ahead", str(months_ahead)),
        ]:
            row = s.query(Config).filter(Config.key==k).first()
            if row:
                row.value = v
            else:
                s.add(Config(key=k, value=v))
        s.commit()
    st.success("Saved.")

st.subheader("Trainer default splits")
with SessionLocal() as s:
    trainers = s.query(Trainer).all()

for t in trainers:
    st.write(f"**{t.name}**")
    col1, col2, col3 = st.columns(3)
    split_trainer = col1.number_input(f"{t.name} trainer split", min_value=0.0, max_value=1.0, value=float(t.split_trainer), key=f"ts_{t.id}")
    split_gym = 1.0 - split_trainer
    col2.write(f"Gym split: **{split_gym:.2f}**")
    if col3.button("Save", key=f"save_{t.id}"):
        with SessionLocal() as s2:
            tt = s2.query(Trainer).get(t.id)
            tt.split_trainer = float(split_trainer)
            tt.split_gym = 1.0 - float(split_trainer)
            s2.commit()
        st.success(f"Saved split for {t.name}.")
