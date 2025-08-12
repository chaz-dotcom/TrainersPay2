import streamlit as st
from db import init_db

st.set_page_config(page_title="Trainer Payouts", page_icon="💸", layout="wide")
init_db(seed=True)

st.title("Trainer Payouts – Home")
st.write("Use the sidebar to navigate: **Dashboard**, **Attendance**, **Agreements**, **Payouts**, **Settings**.")
st.info("Attendance-based revenue (sessions completed × price).")
