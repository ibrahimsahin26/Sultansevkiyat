
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

CSV_PATH = "teslimatlar.csv"

# Başlangıçta CSV dosyasını başlıklarıyla oluştur
if not CSV_PATH or not st.session_state.get("csv_initialized"):
    try:
        pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["tarih", "tur", "sira", "musteri", "not", "genel_not"])
        df.to_csv(CSV_PATH, index=False)
    st.session_state.csv_initialized = True

@st.cache_data
def load_data():
    return pd.read_csv(CSV_PATH)

def save_data(df):
    df.to_csv(CSV_PATH, index=False)

def get_week_dates(selected_date):
    monday = selected_date - timedelta(days=selected_date.weekday())
    return [monday + timedelta(days=i) for i in range(6)]  # Pazartesi - Cumartesi

st.set_page_config(page_title="Haftalık Teslimat Takvimi", layout="centered")
st.title("📅 Haftalık Teslimat Takvimi")

hafta_tarihi = st.date_input("📌 Haftayı Seç", value=datetime.today())
hafta_gunleri = get_week_dates(hafta_tarihi)
df = load_data()

if not df.empty:
    df["tarih"] = pd.to_datetime(df["tarih"], errors="coerce")
    df = df.dropna(subset=["tarih"])

for gun in hafta_gunleri:
    gun_str = gun.strftime("%Y-%m-%d")
    gun_veri = df[df["tarih"] == gun_str]

    st.markdown(f"## 📌 {gun.strftime('%d %B %Y (%A)')}")

    if gun_veri.empty:
        st.info("Henüz planlanmış teslimat yok. Yeni tur ekleyebilirsiniz.")

    turlar = gun_veri["tur"].dropna().unique()
    for tur in sorted(turlar):
        tur_veri = gun_veri[gun_veri["tur"] == tur].sort_values("sira")
        with st.expander(f"🚛 {tur}. Tur", expanded=False):
            st.markdown("**📋 Teslimatlar:**")
            for i, row in tur_veri.iterrows():
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    st.text_input("Müşteri", value=row["musteri"], key=f"musteri_{i}", disabled=True)
                    st.text_input("Not", value=row["not"], key=f"not_{i}", disabled=True)
                with col2:
                    if st.button("Güncelle", key=f"edit_{i}"):
                        st.session_state[f"edit_{i}"] = True
                with col3:
                    if st.button("Sil", key=f"delete_{i}"):
                        df = df.drop(index=i)
                        save_data(df)
                        st.success("Teslimat silindi.")
                        st.experimental_rerun()

            genel_notlar = tur_veri["genel_not"].dropna().unique()
            onceki_not = genel_notlar[0] if len(genel_notlar) > 0 else ""
            yeni_genel_not = st.text_area("📝 Genel Not", value=onceki_not, key=f"genelnot_{gun_str}_{tur}")
            if st.button("💾 Genel Notu Kaydet", key=f"save_note_{gun_str}_{tur}"):
                df.loc[
                    (df["tarih"] == gun_str) & (df["tur"] == tur),
                    "genel_not"
                ] = yeni_genel_not
                save_data(df)
                st.success("Genel not kaydedildi.")
                st.experimental_rerun()

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
        genel_not_yeni = st.text_area("📝 Genel Not (Yeni Tur)", key=f"genelnotyeni_{gun_str}")
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
            st.success("Yeni tur başarıyla kaydedildi.")
            st.experimental_rerun()
