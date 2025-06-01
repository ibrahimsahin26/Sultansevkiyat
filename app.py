import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Teslimat Takvimi", layout="centered")
st.markdown("### 📅 Haftalık Teslimat Takvimi")

CSV_PATH = "teslimatlar.csv"

# İlk kullanımda CSV oluştur
if not os.path.exists(CSV_PATH):
    pd.DataFrame(columns=["tarih", "tur", "sira", "musteri", "not", "genel_not"]).to_csv(CSV_PATH, index=False)

@st.cache_data
def load_data():
    return pd.read_csv(CSV_PATH)

def save_data(df):
    df.to_csv(CSV_PATH, index=False)

def get_week_dates(date):
    monday = date - timedelta(days=date.weekday())
    return [monday + timedelta(days=i) for i in range(6)]  # Pazartesi - Cumartesi

hafta_tarihi = st.date_input("📌 Haftayı Seç", value=datetime.today())
hafta_gunleri = get_week_dates(hafta_tarihi)
df = load_data()

if not df.empty:
    df["tarih"] = pd.to_datetime(df["tarih"], errors="coerce")
    df = df.dropna(subset=["tarih"])

gun_cevir = {
    "Monday": "Pazartesi", "Tuesday": "Salı", "Wednesday": "Çarşamba",
    "Thursday": "Perşembe", "Friday": "Cuma", "Saturday": "Cumartesi"
}

for gun in hafta_gunleri:
    gun_str = gun.strftime("%Y-%m-%d")
    gun_veri = df[df["tarih"] == gun_str]
    gun_baslik = gun.strftime("%d %B %Y (%A)")
    for en, tr in gun_cevir.items():
        gun_baslik = gun_baslik.replace(en, tr)

    st.markdown(f"#### 📌 {gun_baslik}")

    if gun_veri.empty:
        st.info("Henüz planlanmış teslimat yok. Yeni tur ekleyebilirsiniz.")

    turlar = gun_veri["tur"].dropna().unique()
    for tur in sorted(turlar):
        tur_veri = gun_veri[gun_veri["tur"] == tur].sort_values("sira")
        with st.expander(f"🚛 {tur}. Tur"):
            st.dataframe(tur_veri[["sira", "musteri", "not"]].reset_index(drop=True), hide_index=True)
            genel_not = tur_veri["genel_not"].dropna().unique()
            if len(genel_not) > 0:
                st.markdown(f"📌 **Genel Not:** _{genel_not[0]}_")

    with st.expander("➕ Yeni Tur Ekle"):
        yeni_tur_no = st.number_input("Tur No", min_value=1, max_value=10, value=1, key=f"tur_no_{gun_str}")
        teslimat_sayisi = st.number_input("Teslimat Nokta Sayısı", min_value=1, max_value=10, value=3, key=f"teslimat_sayisi_{gun_str}")
        genel_not_yeni = st.text_input("Genel Not", key=f"gnlnot_{gun_str}")

        musteri_listesi = []
        not_listesi = []
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
                "genel_not": [genel_not_yeni] * teslimat_sayisi
            })
            df = pd.concat([df, yeni_kayitlar], ignore_index=True)
            save_data(df)
            st.success("✅ Tur kaydedildi.")
            st.rerun()
