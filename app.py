import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from utils.io import load_data

st.set_page_config(page_title="Teslimat Takvimi", layout="centered")

st.title("📅 Teslimat Takvimi")

DATA_PATH = "data/teslimatlar.csv"

# Veri yükle
df = load_data(DATA_PATH)

# Tarih seçici
secili_tarih = st.date_input("Tarih Seçin", value=datetime.today())

# Gün adını al
gun_adi = secili_tarih.strftime("%A")  # Monday, Tuesday...
gun_tr = {
    "Monday": "Pazartesi", "Tuesday": "Salı", "Wednesday": "Çarşamba",
    "Thursday": "Perşembe", "Friday": "Cuma", "Saturday": "Cumartesi", "Sunday": "Pazar"
}
gun = gun_tr.get(gun_adi, gun_adi)

st.markdown(f"### 📆 {secili_tarih.strftime('%d %B %Y')} - {gun}")

# Bu tarihte tanımlı teslimat var mı?
if df is not None and not df.empty:
    df["tarih"] = pd.to_datetime(df["tarih"], errors="coerce")
    df_tarih = df[df["tarih"] == pd.to_datetime(secili_tarih)]

    if not df_tarih.empty:
        tur_gruplari = df_tarih.groupby("tur_no")
        for tur_no, grup in tur_gruplari:
            st.markdown(f"#### 🚚 {tur_no}. Tur")
            for i, row in grup.iterrows():
                musteri = row["musteri"]
                not_ = row.get("not", "")
                durum = row.get("teslim_durumu", "Planlandı")
                st.markdown(f"- **{musteri}** {'🔖 _'+not_+'_' if not_ else ''} `[{durum}]`")
    else:
        st.info("Bu tarihe ait herhangi bir teslimat planı bulunmamaktadır.")
else:
    st.info("Henüz hiç teslimat verisi girilmemiş.")
