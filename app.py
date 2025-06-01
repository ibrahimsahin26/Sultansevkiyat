import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# Sayfa konfigürasyonu (ilk satırda olmalı)
st.set_page_config(page_title="Teslimat Takvimi", layout="centered")
st.markdown("<h4 style='font-size:22px;'>📅 Haftalık Teslimat Takvimi</h4>", unsafe_allow_html=True)

# CSV yolu
CSV_PATH = "data/teslimatlar.csv"

# CSV yoksa başlıklarla oluştur
if not os.path.exists(CSV_PATH):
    df = pd.DataFrame(columns=["tarih", "tur", "sira", "musteri", "not", "genel_not"])
    df.to_csv(CSV_PATH, index=False)

# Veri yükleme/kaydetme
@st.cache_data
def load_data():
    return pd.read_csv(CSV_PATH)

def save_data(df):
    df.to_csv(CSV_PATH, index=False)

# Haftanın günlerini döndür
def get_week_dates(date):
    monday = date - timedelta(days=date.weekday())
    return [monday + timedelta(days=i) for i in range(6)]  # Pazartesi–Cumartesi

# Gün çevir
gun_cevir = {
    "Monday": "Pazartesi", "Tuesday": "Salı", "Wednesday": "Çarşamba",
    "Thursday": "Perşembe", "Friday": "Cuma", "Saturday": "Cumartesi"
}

# Tarih seçimi
hafta_tarihi = st.date_input("📌 Haftayı Seç", value=datetime.today())
hafta_gunleri = get_week_dates(hafta_tarihi)
df = load_data()

# Tarih dönüşüm
if not df.empty:
    df["tarih"] = pd.to_datetime(df["tarih"], errors="coerce")
    df = df.dropna(subset=["tarih"])

# Gün bazlı görünüm
for gun in hafta_gunleri:
    gun_str = gun.strftime("%Y-%m-%d")
    gun_veri = df[df["tarih"] == gun_str]
    gun_baslik = gun.strftime("%d %B %Y (%A)")
    for en, tr in gun_cevir.items():
        gun_baslik = gun_baslik.replace(en, tr)

    st.markdown(f"<h5 style='margin-top:30px;'>📌 {gun_baslik}</h5>", unsafe_allow_html=True)

    turlar = gun_veri["tur"].dropna().unique()
    if len(turlar) == 0:
        st.info("Henüz planlanmış teslimat yok. Yeni tur ekleyebilirsiniz.")

    for tur in sorted(turlar):
        tur_veri = gun_veri[gun_veri["tur"] == tur].sort_values("sira")
        with st.expander(f"🚛 {tur}. Tur", expanded=False):
            st.data_editor(
                tur_veri[["sira", "musteri", "not"]].reset_index(drop=True),
                column_config={
                    "sira": st.column_config.NumberColumn("Sıra", width="small"),
                    "musteri": st.column_config.TextColumn("Müşteri", width="medium"),
                    "not": st.column_config.TextColumn("Not", width="medium"),
                },
                hide_index=True,
                use_container_width=True,
                disabled=True
            )
            if "genel_not" in tur_veri.columns and tur_veri["genel_not"].notna().any():
                genel = tur_veri["genel_not"].dropna().unique()[0]
                st.markdown(f"<div style='font-size:13px; margin-top:8px;'><b>📌 Genel Not:</b> {genel}</div>", unsafe_allow_html=True)

    # Yeni tur ekleme alanı
    with st.expander("➕ Tur"):
        yeni_tur_no = st.number_input("Tur No", min_value=1, max_value=10, value=1, key=f"tur_{gun_str}")
        teslimat_sayisi = st.number_input("Teslimat Nokta Sayısı", min_value=1, max_value=10, value=3, key=f"adet_{gun_str}")
        genel_not = st.text_area("📌 Genel Not (Tur için)", key=f"genel_{gun_str}")
        musteri_listesi, not_listesi = [], []

        for i in range(teslimat_sayisi):
            musteri = st.text_input("Müşteri", key=f"musteri_{gun_str}_{i}")
            not_ = st.text_input("Not", key=f"not_{gun_str}_{i}")
            musteri_listesi.append(musteri)
            not_listesi.append(not_)

        if st.button("📥 Kaydet", key=f"kaydet_{gun_str}"):
            yeni_kayitlar = pd.DataFrame({
                "tarih": [gun_str] * teslimat_sayisi,
                "tur": [yeni_tur_no] * teslimat_sayisi,
                "sira": list(range(1, teslimat_sayisi + 1)),
                "musteri": musteri_listesi,
                "not": not_listesi,
                "genel_not": [genel_not] * teslimat_sayisi
            })
            df = pd.concat([df, yeni_kayitlar], ignore_index=True)
            save_data(df)
            st.success("✅ Tur kaydedildi.")
            st.rerun()
