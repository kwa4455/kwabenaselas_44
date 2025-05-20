# 🇬🇭 EPA Ghana PM2.5 Monitoring App

A Streamlit-based field data entry app for recording, merging, and calculating air quality observations.

## Features

- Login and role-based access
- Record new observations
- Merge START and STOP entries
- Calculate PM2.5 concentrations
- View and restore deleted records

## Setup

1. Clone this repo
2. Add `secrets.toml` with your Google Sheets credentials
3. Run:

```bash
pip install -r requirements.txt
streamlit run app.py

