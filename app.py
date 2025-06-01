import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

CSV_PATH = "teslimatlar.csv"

# Eğer CSV yoksa oluştur
try:
    pd.read_csv(CSV_PATH)
except FileNotFoundError:
    pd.DataFrame(columns=["tarih", "tur", "sira", "musteri", "not"]).to_csv(CSV_PATH, index=False)

@st.cache_data
def load_data():
    return pd.read_csv(CSV_PATH)

def save_data(df):
    df.to_csv(CSV_PATH, index=False)

def get_week_dates(selected_date):
    monday = selected_date - timedelta(days=selected_date.weekday())
    return [monday + timedelta(days=i) for i in range(6)]  # Pazartesi–Cumartesi

# Başlık
st.set_page_config(page_title="Teslimat Takvimi", layout="centered")
st.title("📅 Haftalık Teslimat Takvimi")

# Tarih Seç
hafta_tarihi = st.date_input("📌 Haftayı Seç", value=datetime.today())
hafta_gunleri = get_week_dates(hafta_tarihi)

# Veriyi yükle
df = load_data()
if not df.empty:
    df["tarih"] = pd.to_datetime(df["tarih"], errors="coerce")
    df = df.dropna(subset=["tarih"])

# Gün gün göster
for gun in hafta_gunleri:
    gun_str = gun.strftime("%Y-%m-%d")
    gun_veri = df[df["tarih"] == gun_str]
    st.markdown(f"### 📌 {gun.strftime('%d %B %Y (%A)')}")

    if gun_veri.empty:
        st.info("Henüz planlanmış teslimat yok.")

    turlar = gun_veri["tur"].dropna().unique()
    for tur in sorted(turlar):
        tur_veri = gun_veri[gun_veri["tur"] == tur].sort_values("sira")
        with st.expander(f"🚛 {tur}. Tur", expanded=False):
            st.dataframe(
                tur_veri[["sira", "musteri", "not"]].reset_index(drop=True),
                hide_index=True,
                use_container_width=True
            )

    with st.expander("➕ Yeni Tur Ekle", expanded=False):
        yeni_tur_no = st.number_input("Tur No", min_value=1, max_value=10, value=1, key=f"tur_no_{gun_str}")
        teslimat_sayisi = st.number_input("Teslimat Noktası", 1, 10, 3, key=f"nokta_{gun_str}")
        musteriler = [st.text_input(f"{i+1}. Müşteri", key=f"m_{gun_str}_{i}") for i in range(teslimat_sayisi)]
        notlar = [st.text_input(f"{i+1}. Not", key=f"n_{gun_str}_{i}") for i in range(teslimat_sayisi)]

        if st.button("📥 Kaydet", key=f"save_{gun_str}"):
            yeni_kayitlar = pd.DataFrame({
                "tarih": [gun_str] * teslimat_sayisi,
                "tur": [yeni_tur_no] * teslimat_sayisi,
                "sira": list(range(1, teslimat_sayisi + 1)),
                "musteri": musteriler,
                "not": notlar
            })
            df = pd.concat([df, yeni_kayitlar], ignore_index=True)
            save_data(df)
            st.success("Yeni tur eklendi.")
            st.experimental_rerun()

