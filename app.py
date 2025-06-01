import os
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# 🔄 İngilizce gün isimlerini Türkçeye çevirme
GUN_MAP = {
    "Monday": "Pazartesi",
    "Tuesday": "Salı",
    "Wednesday": "Çarşamba",
    "Thursday": "Perşembe",
    "Friday": "Cuma",
    "Saturday": "Cumartesi",
    "Sunday": "Pazar",
}

CSV_PATH = "teslimatlar.csv"
if not os.path.exists(CSV_PATH):
    pd.DataFrame(columns=["tarih", "tur", "sira", "musteri", "not"]).to_csv(CSV_PATH, index=False)

def load_data():
    return pd.read_csv(CSV_PATH)

def save_data(df):
    df.to_csv(CSV_PATH, index=False)

def haftanin_gunleri(tarih):
    baslangic = tarih - timedelta(days=tarih.weekday())
    return [baslangic + timedelta(days=i) for i in range(6)]  # Pazartesi-Cumartesi

def gun_bazli_goster(gun, df):
    st.markdown(f"### 
