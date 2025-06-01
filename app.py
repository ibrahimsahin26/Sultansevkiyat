import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

# Veri dosyası yolu
CSV_PATH = "teslimatlar.csv"

# CSV dosyası yoksa başlıklarıyla oluştur
if not CSV_PATH or not st.session_state.get("csv_initialized"):
    try:
        pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["tarih", "tur", "sira", "musteri", "not"])
        df.to_csv(CSV_PATH, index=False)
    st.session_state.csv_initialized = True

# Veriyi yükle
@st.cache_data
def load_data():
    return pd.read_csv(CSV_PATH)

def save_data(df):
    df.to_csv(CSV_PATH, index=False)

def get_week_dates(selected_date):
    monday = selected_date - timedelta(days=selected_date.weekday())
    return [monday + timedelta(days=i) for i in range(6)]  # Pazartesi - Cumartesi

# Sayfa başlığı
st.set_page_config(page_title="Haftalık Teslimat Takvimi", layout="centered")
st.title("📅 Haftalık Teslimat Takvimi")

# Tarih seçimi
hafta_tarihi = st.date_input("📌 Haftayı Seç", value=datetime.today())
hafta_gunleri = get_week_dates(hafta_tarihi)

# Veri yükle
df = load_data()

# Tarih sütununu datetime'a çevir
if not df.empty:
    df["tarih"] = pd.to_datetime(df["tarih"], errors="coerce")
    df = df.dropna(subset=["tarih"])

# Günleri sırayla göster
for gun in hafta_gunleri:
    gun_str = gun.strftime("%Y-%m-%d")
    gun_veri = df[df["tarih"] == gun_str]

    st.markdown(f"## 📌 {gun.strftime('%d %B %Y (%A)')}")

    if gun_veri.empty:
        st.info("Henüz planlanmış teslimat yok. Yeni tur ekleyebilirsiniz.")

    turlar = gun_veri["tur"].dropna().unique()
    for tur in sorted(turlar):
        tur_veri = gun_veri[gun_veri["tur"] == tur].sort_values("sira")
        with st.expander(f"🚛 {tur}. Tur"):
            st.dataframe(
                tur_veri[["sira", "musteri", "not"]].reset_index(drop=True),
                hide_index=True,
                use_container_width=True
            )

    with st.expander("➕ Yeni Tur Ekle"):
        yeni_tur_no = st.number_input("Tur No", min_value=1, max_value=10, value=1, key=f"tur_no_{gun_str}")
        teslimat_sayisi = st.number_input("Teslimat Nokta Sayısı", min_value=1, max_value=10, value=3, key=f"teslimat_sayisi_{gun_str}")

        musteri_listesi = []
        not_listesi = []
        for i in range(teslimat_sayisi):
            musteri = st.text_input(f"Müşteri", key=f"musteri_{gun_str}_{i}")
            not_ = st.text_input(f"Not", key=f"not_{gun_str}_{i}")
            musteri_listesi.append(musteri)
            not_listesi.append(not_)

        if st.button("📥 Kaydet", key=f"kaydet_{gun_str}"):
            yeni_kayitlar = pd.DataFrame({
                "tarih": [gun_str] * teslimat_sayisi,
                "tur": [yeni_tur_no] * teslimat_sayisi,
                "sira": list(range(1, teslimat_sayisi + 1)),
                "musteri": musteri_listesi,
                "not": not_listesi
            })
            df = pd.concat([df, yeni_kayitlar], ignore_index=True)
            save_data(df)
            st.success("Yeni tur başarıyla kaydedildi. Sayfa yenileniyor...")
            st.experimental_rerun()
