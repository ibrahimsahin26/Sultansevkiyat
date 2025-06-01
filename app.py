import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.io import load_data, save_data

DATA_PATH = "data/teslimatlar.csv"

st.set_page_config(page_title="Teslimat Takvimi", layout="wide")
st.title("📅 Haftalık Teslimat Takvimi")

# 📅 Bugünün haftasını ve tarih aralığını hesapla
bugun = date.today()
hafta_basi = bugun - timedelta(days=bugun.weekday())  # Pazartesi
hafta_sonu = hafta_basi + timedelta(days=5)  # Cumartesi

hafta_label = f"{hafta_basi.strftime('%d %B')} - {hafta_sonu.strftime('%d %B %Y')}"
st.subheader(f"📆 {hafta_label} Haftası")

df = load_data(DATA_PATH)
df["tarih"] = pd.to_datetime(df["tarih"], errors="coerce")
df = df.dropna(subset=["tarih"])
df = df.sort_values(by=["tarih", "tur", "sira"])

# 📅 Haftalık veri filtrele
mask = (df["tarih"] >= pd.to_datetime(hafta_basi)) & (df["tarih"] <= pd.to_datetime(hafta_sonu))
df_hafta = df[mask]

# 📌 Her gün için akordeonlu görünüm
for i in range(6):  # Pazartesi - Cumartesi
    gun_tarih = hafta_basi + timedelta(days=i)
    gun_label = gun_tarih.strftime("%A - %d %B")
    gun_df = df_hafta[df_hafta["tarih"] == pd.to_datetime(gun_tarih)]

    with st.expander(f"📍 {gun_label}"):
        if gun_df.empty:
            st.info("Bu gün için planlanmış teslimat yok.")
        else:
            # Tur gruplarına göre sırala
            for tur_adi, grup in gun_df.groupby("tur"):
                st.markdown(f"#### 🚚 {tur_adi}")

                edit_df = grup[["sira", "musteri", "not"]].reset_index(drop=True)
                edited = st.data_editor(edit_df, num_rows="dynamic", key=f"editor_{gun_tarih}_{tur_adi}")

                if st.button("💾 Değişiklikleri Kaydet", key=f"save_{gun_tarih}_{tur_adi}"):
                    for idx, row in edited.iterrows():
                        mask_update = (
                            (df["tarih"] == gun_tarih) &
                            (df["tur"] == tur_adi) &
                            (df["sira"] == row["sira"])
                        )
                        df.loc[mask_update, "musteri"] = row["musteri"]
                        df.loc[mask_update, "not"] = row["not"]

                    save_data(df, DATA_PATH)
                    st.success("Değişiklikler kaydedildi.")
