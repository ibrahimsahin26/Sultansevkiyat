import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import locale
import os

# Sayfa konfigürasyonu
st.set_page_config(page_title="Teslimat Takvimi", layout="centered")

# Tarih formatı Türkçe için yerelleştirme
locale.setlocale(locale.LC_TIME, "tr_TR.UTF-8") if os.name != 'nt' else None

# CSV dosya yolu
CSV_PATH = "teslimatlar.csv"

# CSV yoksa oluştur
if not os.path.exists(CSV_PATH):
    pd.DataFrame(columns=["tarih", "tur", "sira", "musteri", "not"]).to_csv(CSV_PATH, index=False)

# Veriyi oku
@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(CSV_PATH)

def save_data(df):
    df.to_csv(CSV_PATH, index=False)

# Haftanın günlerini ve tarihlerini hesapla
@st.cache_data
def get_week_dates(reference_date):
    start_of_week = reference_date - timedelta(days=reference_date.weekday())
    return [start_of_week + timedelta(days=i) for i in range(6)]  # Pazartesi - Cumartesi

# Tarih seçimi
hafta_baslangic = st.date_input("📌 Haftayı Seç", value=datetime.today())
hafta_gunleri = get_week_dates(hafta_baslangic)

# Veri yükle
df = load_data()
df["tarih"] = pd.to_datetime(df["tarih"], errors="coerce")

# Stil
st.markdown("""
    <style>
    section.main > div { padding-top: 1rem; }
    div[data-testid="column"] div[style*="flex"] { padding: 4px; }
    .small-input input { font-size: 14px; height: 32px; padding: 4px; }
    </style>
""", unsafe_allow_html=True)

# Başlık
st.title("📅 Haftalık Teslimat Takvimi")

for gun in hafta_gunleri:
    st.markdown(f"## 📌 {gun.strftime('%d %B %Y (%A)')}")

    gun_df = df[df["tarih"] == pd.to_datetime(gun.date())]

    if gun_df.empty:
        st.info("Henüz planlanmış teslimat yok. Yeni tur ekleyebilirsiniz.")

    # Tur Ekleme
    with st.expander("➕ Yeni Tur Ekle"):
        yeni_tur_no = st.number_input("Tur No", min_value=1, max_value=10, value=1, key=f"tur_{gun}")
        teslimat_adet = st.number_input("Teslimat Nokta Sayısı", min_value=1, max_value=20, value=3, key=f"adet_{gun}")

        musteri_list = []
        for i in range(teslimat_adet):
            col1, col2 = st.columns([2, 3])
            with col1:
                musteri = st.text_input(f"Müşteri", key=f"musteri_{gun}_{i}")
            with col2:
                not_ = st.text_input("Not", key=f"not_{gun}_{i}")
            if musteri.strip():
                musteri_list.append({"musteri": musteri.strip(), "not": not_.strip(), "sira": i + 1})

        if st.button("💾 Kaydet", key=f"kaydet_{gun}"):
            yeni_kayitlar = pd.DataFrame([{
                "tarih": gun.date(),
                "tur": yeni_tur_no,
                "sira": musteri["sira"],
                "musteri": musteri["musteri"],
                "not": musteri["not"]
            } for musteri in musteri_list])
            df = pd.concat([df, yeni_kayitlar], ignore_index=True)
            save_data(df)
            st.success("Tur kaydedildi.")
            st.rerun()

    # Mevcut Turların Gösterimi
    for tur in sorted(gun_df["tur"].unique()):
        tur_df = gun_df[gun_df["tur"] == tur].sort_values("sira")
        with st.expander(f"🚚 {tur}. Tur"):
            for _, row in tur_df.iterrows():
                col1, col2 = st.columns([2, 3])
                col1.markdown(f"**{row['sira']}. {row['musteri']}**")
                if row["not"]:
                    col2.markdown(f"📌 _{row['not']}_")
