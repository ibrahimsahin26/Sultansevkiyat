import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

CSV_PATH = "teslimatlar.csv"

# Veri yükleme ve kaydetme
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(CSV_PATH)
        df["tarih"] = pd.to_datetime(df["tarih"], errors="coerce")
        df = df.dropna(subset=["tarih"])
        return df
    except:
        return pd.DataFrame(columns=["tarih", "tur", "sira", "musteri", "not"])

def save_data(df):
    df.to_csv(CSV_PATH, index=False)

def get_week_dates(date):
    monday = date - timedelta(days=date.weekday())
    return [monday + timedelta(days=i) for i in range(6)]

# Sayfa ayarları
st.set_page_config(page_title="Teslimat Güncelleme", layout="centered")
st.title("📋 Teslimat Güncelleme Paneli")

hafta_tarihi = st.date_input("📆 Haftayı Seç", value=datetime.today())
hafta_gunleri = get_week_dates(hafta_tarihi)
df = load_data()

for gun in hafta_gunleri:
    st.markdown(f"### 📌 {gun.strftime('%d %B %Y (%A)')}")
    gun_df = df[df["tarih"] == gun.strftime("%Y-%m-%d")]

    if gun_df.empty:
        st.info("Bu gün için teslimat yok.")
        continue

    for tur in sorted(gun_df["tur"].dropna().unique()):
        st.markdown(f"#### 🚚 {tur}. Tur")
        tur_df = gun_df[gun_df["tur"] == tur].sort_values("sira")

        for i, row in tur_df.iterrows():
            with st.expander(f"{row['sira']}. {row['musteri']}"):
                musteri = st.text_input("Müşteri Adı", value=row["musteri"], key=f"musteri_{i}")
                not_ = st.text_input("Not", value=row["not"], key=f"not_{i}")
                sira = st.number_input("Sıra No", min_value=1, value=int(row["sira"]), key=f"sira_{i}")

                yeni_tarih = st.date_input("Yeni Tarih", value=row["tarih"], key=f"tarih_{i}")
                yeni_tur = st.number_input("Yeni Tur", min_value=1, max_value=10, value=int(row["tur"]), key=f"tur_{i}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📥 Güncelle", key=f"guncelle_{i}"):
                        df.drop(index=i, inplace=True)
                        yeni_kayit = pd.DataFrame.from_records([{
                            "tarih": yeni_tarih.strftime("%Y-%m-%d"),
                            "tur": yeni_tur,
                            "sira": sira,
                            "musteri": musteri,
                            "not": not_
                        }])
                        df = pd.concat([df, yeni_kayit], ignore_index=True)
                        save_data(df)
                        st.success("Kayıt güncellendi")
                        st.experimental_rerun()
                with col2:
                    if st.button("🗑️ Sil", key=f"sil_{i}"):
                        df.drop(index=i, inplace=True)
                        save_data(df)
                        st.success("Kayıt silindi")
                        st.experimental_rerun()
