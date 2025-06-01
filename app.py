import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# CSV dosya yolu
CSV_PATH = "teslimatlar.csv"

# Ön tanımlı kolonlar
COLUMNS = ["tarih", "tur_no", "sira", "musteri", "not"]

# Veri çekme/yükleme
if not os.path.exists(CSV_PATH):
    pd.DataFrame(columns=COLUMNS).to_csv(CSV_PATH, index=False)

df = pd.read_csv(CSV_PATH)
df["tarih"] = pd.to_datetime(df["tarih"], errors="coerce")
df = df.dropna(subset=["tarih"])

# Üstte stil ayarları
st.markdown("""
    <style>
    .small-text { font-size: 13px !important; }
    .day-header { font-size: 18px !important; font-weight: bold; }
    .tur-table td { font-size: 13px !important; padding: 2px 4px; }
    .stNumberInput > div { max-width: 80px; }
    </style>
""", unsafe_allow_html=True)

# Gün adları türkçe
gun_isimleri = {
    "Monday": "Pazartesi", "Tuesday": "Salı", "Wednesday": "Çarşamba",
    "Thursday": "Perşembe", "Friday": "Cuma", "Saturday": "Cumartesi", "Sunday": "Pazar"
}

# Sayfa
st.set_page_config(page_title="Teslimat Takvimi", layout="centered")
st.title("📅 Haftalık Teslimat Takvimi")

hafta_baslangic = st.date_input("📌 Haftayı Seç", value=datetime.today())
hafta_baslangic = hafta_baslangic - timedelta(days=hafta_baslangic.weekday())

for i in range(6):
    tarih = hafta_baslangic + timedelta(days=i)
    gun = tarih.strftime("%A")
    gun_tr = gun_isimleri.get(gun, gun)

    st.markdown(f"## 📌 {tarih.strftime('%d %B %Y')} ({gun_tr})")
    gun_df = df[df["tarih"] == tarih]

    if gun_df.empty:
        st.info("Henüz planlanmış teslimat yok. Yeni tur ekleyebilirsiniz.")

    turlar = gun_df["tur_no"].dropna().unique()
    for tur in sorted(turlar):
        tur_data = gun_df[gun_df["tur_no"] == tur].sort_values("sira")
        with st.expander(f"🚚 {tur}. Tur"):
            for _, row in tur_data.iterrows():
                col1, col2, col3 = st.columns([0.1, 0.5, 0.4])
                with col1:
                    st.markdown(f"<span class='small-text'>{int(row['sira'])}</span>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<span class='small-text'>{row['musteri']}</span>", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"<span class='small-text'>{row['not']}</span>", unsafe_allow_html=True)

    with st.expander("➕ Yeni Tur Ekle"):
        yeni_tur_no = st.number_input("Tur No", min_value=1, max_value=10, value=1, key=f"tur_{i}")
        teslimat_adet = st.number_input("Teslimat Nokta Sayısı", min_value=1, max_value=20, value=3, key=f"adet_{i}")

        yeni_veriler = []
        for j in range(teslimat_adet):
            col1, col2 = st.columns([0.5, 0.5])
            musteri = col1.text_input("Müşteri", key=f"musteri_{i}_{j}")
            not_ = col2.text_input("Not", key=f"not_{i}_{j}")
            if musteri.strip():
                yeni_veriler.append({
                    "tarih": tarih,
                    "tur_no": yeni_tur_no,
                    "sira": j+1,
                    "musteri": musteri.strip(),
                    "not": not_.strip()
                })

        if st.button(f"💾 {tarih.strftime('%d %B')} için Turu Kaydet", key=f"btn_{i}"):
            if yeni_veriler:
                df = pd.concat([df, pd.DataFrame(yeni_veriler)], ignore_index=True)
                df.to_csv(CSV_PATH, index=False)
                st.success("Tur eklendi.")
                st.experimental_rerun()
