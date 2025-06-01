import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Veri dosyası
CSV_PATH = "teslimatlar.csv"

# Dosya yoksa oluştur
if not st.session_state.get("veri_yüklendi"):
    try:
        df = pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["tarih", "gun", "tur", "sira", "musteri", "not"])
        df.to_csv(CSV_PATH, index=False)
    st.session_state["veri_yüklendi"] = True

# Veri oku
df = pd.read_csv(CSV_PATH)
df["tarih"] = pd.to_datetime(df["tarih"], errors="coerce")

# Başlık
st.set_page_config(page_title="Haftalık Teslimat Takvimi")
st.title("📅 Haftalık Teslimat Takvimi")

# Bugün seçimi ve hafta hesaplama
secili_tarih = st.date_input("📌 Haftayı Seç", datetime.today())
hafta_basi = secili_tarih - timedelta(days=secili_tarih.weekday())
hafta_gunu_listesi = [hafta_basi + timedelta(days=i) for i in range(6)]

# Günlere göre gösterim
for gun_tarihi in hafta_gunu_listesi:
    gun_ad = gun_tarihi.strftime("%A")  # Monday, Tuesday...
    st.markdown(f"## 📌 {gun_tarihi.strftime('%d %B %Y')} ({gun_ad})")

    gun_df = df[df["tarih"] == gun_tarihi]

    # O gün veri yoksa uyarı
    if gun_df.empty:
        st.info("Henüz planlanmış teslimat yok. Yeni tur ekleyebilirsiniz.")
    
    # Mevcut tur numaraları
    turlar = sorted(gun_df["tur"].dropna().unique())

    for tur in turlar:
        tur_df = gun_df[gun_df["tur"] == tur].sort_values("sira")

        with st.expander(f"🚛 {tur}. Tur"):
            st.table(tur_df[["sira", "musteri", "not"]])

    # Yeni Tur Ekleme
    with st.expander("➕ Yeni Tur Ekle"):
        yeni_tur_no = st.number_input("Tur No", min_value=1, max_value=10, value=1)
        teslimat_sayisi = st.number_input("Teslimat Nokta Sayısı", min_value=1, max_value=20, value=3)

        yeni_kayitlar = []
        for i in range(teslimat_sayisi):
            col1, col2 = st.columns([0.5, 0.5])
            with col1:
                musteri = st.text_input(f"{i+1}. Müşteri", key=f"m_{gun_tarihi}_{i}")
            with col2:
                not_ = st.text_input(f"{i+1}. Not", key=f"n_{gun_tarihi}_{i}")
            if musteri.strip():
                yeni_kayitlar.append({
                    "tarih": gun_tarihi,
                    "gun": gun_ad,
                    "tur": yeni_tur_no,
                    "sira": i + 1,
                    "musteri": musteri.strip(),
                    "not": not_.strip()
                })

        if st.button("💾 Kaydet", key=f"kaydet_{gun_tarihi}"):
            if yeni_kayitlar:
                yeni_df = pd.DataFrame(yeni_kayitlar)
                df = pd.concat([df, yeni_df], ignore_index=True)
                df.to_csv(CSV_PATH, index=False)
                st.success("Yeni teslimat eklendi. Sayfayı yenileyin.")
            else:
                st.warning("En az bir müşteri bilgisi girilmelidir.")

    st.markdown("---")
