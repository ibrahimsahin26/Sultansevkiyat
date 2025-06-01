import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# Veri dosyası yolu
DATA_PATH = "data/teslimatlar.csv"

# Eğer yoksa boş CSV oluştur
if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=["tarih", "gun", "tur", "sira", "musteri", "not"]).to_csv(DATA_PATH, index=False)

# Veriyi yükle
veri = pd.read_csv(DATA_PATH)
veri["tarih"] = pd.to_datetime(veri["tarih"], errors="coerce")

# Başlık
st.title("\ud83d\uddd3\ufe0f Haftal\u0131k Teslimat Takvimi")

# Bugünün tarihinden haftaya göre başlang\u0131c ve biti\u015f
bugun = datetime.today()
baslangic = bugun - timedelta(days=bugun.weekday())
bitis = baslangic + timedelta(days=5)

st.subheader(f"\ud83d\uddd3\ufe0f {baslangic.strftime('%d %B')} - {bitis.strftime('%d %B %Y')} Haftas\u0131")

# G\u00fcn isimleri ve tarihleri
haftalik_gunler = [(baslangic + timedelta(days=i)) for i in range(6)]

# Her g\u00fcn i\u00e7in accordion ve i\u00e7erik
for gun_tarih in haftalik_gunler:
    gun_adi = gun_tarih.strftime("%A")
    g_etiket = f"{gun_adi} - {gun_tarih.strftime('%d %B')}"

    with st.expander(g_etiket):
        gun_veri = veri[veri["tarih"] == gun_tarih]
        mevcut_tur_sayisi = gun_veri["tur"].max() if not gun_veri.empty else 0

        for tur in range(1, int(mevcut_tur_sayisi) + 1):
            st.markdown(f"#### \ud83d\ude9a {tur}. Tur")
            tur_df = gun_veri[gun_veri["tur"] == tur].sort_values("sira")
            for _, row in tur_df.iterrows():
                st.write(f"{int(row['sira'])}. {row['musteri']}")
                if pd.notna(row['not']) and row['not'] != "":
                    with st.expander("\ud83d\udccc Notu G\u00f6ster"):
                        st.markdown(row['not'])

        # Yeni tur ekle
        st.markdown("---")
        if st.button(f"\u2795 {gun_adi} i\u00e7in Yeni Tur Ekle", key=f"tur_ekle_{gun_adi}"):
            with st.form(f"form_{gun_adi}"):
                yeni_tur_no = int(mevcut_tur_sayisi) + 1
                st.markdown(f"### \ud83d\ude9a Yeni {yeni_tur_no}. Tur")
                satir_sayisi = st.slider("Ka\u00e7 teslimat noktas\u0131 eklenecek?", 1, 10, 3)
                yeni_kayitlar = []
                for i in range(satir_sayisi):
                    musteri = st.text_input(f"{i+1}. M\u00fc\u015fteri", key=f"m_{gun_adi}_{i}")
                    notu = st.text_area("Not", key=f"n_{gun_adi}_{i}", placeholder="(Opsiyonel)")
                    if musteri:
                        yeni_kayitlar.append({
                            "tarih": gun_tarih.strftime("%Y-%m-%d"),
                            "gun": gun_adi,
                            "tur": yeni_tur_no,
                            "sira": i + 1,
                            "musteri": musteri,
                            "not": notu
                        })
                if st.form_submit_button("Kaydet") and yeni_kayitlar:
                    yeni_df = pd.DataFrame(yeni_kayitlar)
                    tum_df = pd.concat([veri, yeni_df], ignore_index=True)
                    tum_df.to_csv(DATA_PATH, index=False)
                    st.success("Yeni tur eklendi.")
                    st.experimental_rerun()
