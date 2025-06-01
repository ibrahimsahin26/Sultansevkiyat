# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# Veri dosyası
DATA_PATH = "data/teslimatlar.csv"

# CSV yoksa oluştur
if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=["tarih", "gun", "tur", "sira", "musteri", "not"]).to_csv(DATA_PATH, index=False)

# Veri yükle
@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

def save_data(df):
    df.to_csv(DATA_PATH, index=False)

# Sayfa başlığı
st.set_page_config(page_title="Teslimat Takvimi", layout="wide")
st.title("📅 Haftalık Teslimat Takvimi")

# Tarih seçici
secilen_tarih = st.date_input("Haftayı Seçin", value=datetime.today())
baslangic = secilen_tarih - timedelta(days=secilen_tarih.weekday())
hafta_gunleri = [(baslangic + timedelta(days=i)) for i in range(6)]
gun_adlari = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi"]

# Mevcut veriler
df = load_data()
df["tarih"] = pd.to_datetime(df["tarih"], errors="coerce")

# Hafta aralığını göster
bitis = baslangic + timedelta(days=5)
st.subheader(f"📅 {baslangic.strftime('%d %B')} - {bitis.strftime('%d %B %Y')} Haftası")

# Her gün için tablo
for gun_tarih, gun_adi in zip(hafta_gunleri, gun_adlari):
    st.markdown(f"#### 📌 {gun_adi} – {gun_tarih.strftime('%d %B %Y')}")
    gun_df = df[df["tarih"] == pd.to_datetime(gun_tarih)]

    for tur_no in range(1, 4):
        tur_df = gun_df[gun_df["tur"] == tur_no].sort_values("sira")
        with st.expander(f"🚚 {tur}"):
