# Trainer Payout Web App (Streamlit)

A lightweight internal web platform for managing personal trainer payouts at your gym.

## Features
- Agreements: client ↔ trainer packages (session length, price)
- Attendance: log sessions; revenue = sum(attended × price)
- Dashboard: per‑trainer revenue, YTD, and projections; adjustable split (70/30 default) or custom
- Payouts: monthly payout/retain calculations
- Settings: global assumptions (retention, growth, months ahead), and trainer default splits

## Quick Start
1. Install requirements
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app
   ```bash
   streamlit run app.py
   ```

The app creates a local SQLite database at `trainer_payout.db` on first run with demo data.
