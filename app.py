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
st.title("\U0001F4C5 Haftalık Teslimat Takvimi")

# Tarih Seç
hafta_tarihi = st.date_input("\U0001F4CC Haftayı Seç", value=datetime.today())
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
    st.markdown(f"### \U0001F4CC {gun.strftime('%d %B %Y (%A)')}")

    if gun_veri.empty:
        st.info("Henüz planlanmış teslimat yok.")

    turlar = gun_veri["tur"].dropna().unique()
    for tur in sorted(turlar):
        tur_veri = gun_veri[gun_veri["tur"] == tur].sort_values("sira")
        with st.expander(f"\U0001F69B {tur}. Tur", expanded=False):
            for idx, row in tur_veri.iterrows():
                col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 1, 1])
                with col1:
                    sira_yeni = st.number_input("Sıra", value=int(row["sira"]), min_value=1, step=1, key=f"sira_{idx}")
                with col2:
                    musteri_yeni = st.text_input("Müşteri", value=row["musteri"], key=f"musteri_{idx}")
                with col3:
                    not_yeni = st.text_input("Not", value=row["not"], key=f"not_{idx}")
                with col4:
                    if st.button("Güncelle", key=f"update_{idx}"):
                        df.at[idx, "sira"] = sira_yeni
                        df.at[idx, "musteri"] = musteri_yeni
                        df.at[idx, "not"] = not_yeni
                        save_data(df)
                        st.success("Güncellendi.")
                        st.experimental_rerun()
                with col5:
                    if st.button("Sil", key=f"delete_{idx}"):
                        df = df.drop(index=idx).reset_index(drop=True)
                        save_data(df)
                        st.success("Silindi.")
                        st.experimental_rerun()

    with st.expander("➕ Yeni Tur Ekle", expanded=False):
        yeni_tur_no = st.number_input("Tur No", min_value=1, max_value=10, value=1, key=f"tur_no_{gun_str}")
        teslimat_sayisi = st.number_input("Teslimat Noktası", 1, 10, 3, key=f"nokta_{gun_str}")
        musteriler = [st.text_input(f"{i+1}. Müşteri", key=f"m_{gun_str}_{i}") for i in range(teslimat_sayisi)]
        notlar = [st.text_input(f"{i+1}. Not", key=f"n_{gun_str}_{i}") for i in range(teslimat_sayisi)]

        if st.button("\U0001F4E5 Kaydet", key=f"save_{gun_str}"):
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
